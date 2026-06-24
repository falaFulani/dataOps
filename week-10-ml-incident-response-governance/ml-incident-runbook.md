# ML Incident Response Runbook

**Purpose:** A complete operational runbook for ML-specific incidents. Covers detection, triage, response, escalation, and communication for all ML failure modes.

**Audience:** ML Support Lead, MLOps on-call engineers, platform team.

**Last updated:** _(update when you customize this)_

---

## Incident Classification Matrix

### Severity Levels

| Severity | Definition | Response time | Example |
|----------|-----------|---------------|---------|
| **P1 — Critical** | Model serving errors affecting users, or bias/compliance violation | Immediate (< 15 min) | Model endpoint down, discriminatory outputs detected |
| **P2 — High** | Significant accuracy degradation detected, data quality failure | < 1 hour | Accuracy dropped 15%+, upstream data pipeline broken |
| **P3 — Medium** | Drift detected with minor impact, pipeline failure with fallback | < 4 hours | Data drift above threshold, retraining pipeline failed |
| **P4 — Low** | Informational drift alerts, scheduled maintenance | Next business day | Minor feature drift, model approaching review date |

### Incident Type × Severity Matrix

| Incident Type | P1 (Critical) | P2 (High) | P3 (Medium) | P4 (Low) |
|---------------|---------------|-----------|-------------|----------|
| **Serving errors** | Endpoint down, all requests failing | Intermittent 5xx, latency > 5x normal | Occasional timeouts | Latency slightly elevated |
| **Accuracy degradation** | Accuracy below safety threshold | Accuracy dropped 10%+ | Accuracy dropped 5–10% | Accuracy trending down slightly |
| **Data quality** | Critical features all null/corrupted | Major schema break, stale by 24h+ | Minor schema drift, stale by <12h | Data freshness warning |
| **Drift** | Extreme drift + accuracy collapse | Significant drift + accuracy impact | Drift detected, no accuracy impact yet | Minor distribution shift |
| **Pipeline failure** | No fallback, stale model in danger zone | Pipeline failed, manual retrain needed | Pipeline failed, recent model still valid | Pipeline slow, not failed |
| **Bias/fairness** | Active bias in production predictions | Bias detected in staging/shadow | Bias metrics trending toward threshold | Scheduled fairness audit due |

---

## Incident Response Procedures

---

### Scenario 1: "Model accuracy dropped overnight"

**Detection:** Accuracy monitoring alert fires (from Week 9 SLOs).

#### Triage Steps

```
1. CONFIRM the alert
   - Check monitoring dashboard: is accuracy actually below threshold?
   - Rule out: monitoring bug, metric calculation error, small sample size
   - Check: has enough prediction volume passed to make this statistically significant?

2. ASSESS impact
   - How many predictions were affected?
   - What's the business impact of wrong predictions?
   - Are affected predictions still being served right now?
   - Is this trending worse or stabilizing?

3. DETERMINE root cause category
   ┌─────────────────────────────────────────────────────────────────┐
   │ Check data quality first:                                       │
   │   - Are upstream features arriving correctly?                   │
   │   - Any null spikes? Schema changes? Stale data?               │
   │   - If YES → This is a data quality incident (go to Scenario 2)│
   │                                                                 │
   │ Check for drift:                                                │
   │   - Run drift report on recent vs training data                 │
   │   - Has input distribution shifted significantly?               │
   │   - If YES → This is a drift incident (go to retraining tree)  │
   │                                                                 │
   │ Check for code/config changes:                                  │
   │   - Was anything deployed recently?                             │
   │   - Any config changes to feature pipelines?                    │
   │   - If YES → This is a deployment incident (standard rollback)  │
   │                                                                 │
   │ Check for external events:                                      │
   │   - Holiday, market event, seasonal shift?                      │
   │   - If YES → May be temporary, monitor closely                  │
   └─────────────────────────────────────────────────────────────────┘

4. RESPOND based on root cause
   - Data quality → Fix data pipeline, rollback model if accuracy is critical
   - Drift → Evaluate: retrain vs rollback (see retraining-decision-tree.md)
   - Code change → Rollback deployment
   - External event → Document, monitor, prepare contingency

5. COMMUNICATE
   - Notify stakeholders (see communication templates below)
   - Update incident channel
   - Document timeline as you go (for postmortem)
```

#### Timing Guidelines

| Step | Target time | Notes |
|------|------------|-------|
| Confirm alert | < 5 minutes | Is this real? |
| Assess impact | < 15 minutes | How bad, how many affected? |
| Root cause category | < 30 minutes | Data? Drift? Code? External? |
| Initial response | < 1 hour | Rollback, fix, or escalate |
| Full resolution | < 4 hours (P2) | Retrain, deploy fix, verify |

---

### Scenario 2: "Data pipeline serving stale data"

**Detection:** Data freshness check alert, feature pipeline monitoring, or downstream accuracy drop.

#### Triage Steps

```
1. CONFIRM staleness
   - Check feature store / data pipeline timestamps
   - When was data last successfully refreshed?
   - How stale is it? (hours vs days matters)

2. ASSESS impact on model
   - Is the model still receiving features? (stale but present vs missing entirely)
   - Are stale features causing predictions to degrade?
   - Which features are affected? Are they high-importance?

3. DIAGNOSE pipeline failure
   - Check orchestrator (Airflow/Prefect/etc.) for job failures
   - Check upstream data sources — are they producing?
   - Check for: auth failures, schema changes, network issues, resource limits
   - Was there a deployment to the pipeline recently?

4. RESPOND
   If staleness < 12 hours AND model accuracy still within SLO:
     → Fix pipeline, monitor model accuracy
     
   If staleness > 12 hours OR model accuracy degrading:
     → Fix pipeline AND consider:
       - Switching to fallback model (if available)
       - Serving cached predictions (if appropriate)
       - Disabling model endpoint (if predictions are harmful when stale)

5. VERIFY recovery
   - Pipeline producing fresh data again
   - Model accuracy recovering
   - No backfill needed? Or do you need to reprocess missed data?
```

#### Key Questions

- Does the model gracefully handle missing features? (returns default, errors out, or silently degrades?)
- Is there a fallback model trained on more stable features?
- How quickly does accuracy degrade with stale data? (some models are robust for hours, others aren't)

---

### Scenario 3: "Drift detected, no accuracy drop yet"

**Detection:** Drift monitoring alert (Evidently, Arize, or custom). Statistical test shows distribution shift but accuracy SLO is still met.

#### Triage Steps

```
1. CONFIRM drift is real
   - Check which features drifted and by how much
   - Is it a gradual shift or sudden jump?
   - Is the sample size sufficient for the statistical test?
   - Rule out: seasonal patterns, expected business cycles

2. ASSESS risk
   - Which features drifted? High-importance or low-importance?
   - How far has the distribution moved? (KL divergence, PSI score)
   - Historical pattern: does accuracy typically lag drift by days/weeks?
   - Is this likely to get worse or is it stabilizing?

3. DECIDE: proactive action or monitor?

   ┌─────────────────────────────────────────────────────────┐
   │ MONITOR ONLY if:                                        │
   │   - Drift is in low-importance features                 │
   │   - Shift is small (PSI < 0.1)                          │
   │   - Accuracy is comfortably within SLO                  │
   │   - Pattern looks like it's stabilizing                 │
   │                                                         │
   │ PREPARE TO RETRAIN if:                                  │
   │   - Drift is in high-importance features                │
   │   - Shift is moderate (PSI 0.1–0.25)                    │
   │   - Historical pattern shows accuracy follows drift     │
   │   - Trend is accelerating                               │
   │                                                         │
   │ RETRAIN NOW if:                                         │
   │   - Drift is severe (PSI > 0.25)                        │
   │   - Multiple important features affected                │
   │   - You've seen this pattern before → accuracy drops    │
   │   - Business can't afford to wait for accuracy to drop  │
   └─────────────────────────────────────────────────────────┘

4. DOCUMENT
   - Log drift detection in model health record
   - Note decision rationale (why you chose to monitor/retrain/wait)
   - Set review date if choosing to monitor
```

#### Communication

Drift without accuracy drop is typically **P4 (Low)** — no stakeholder escalation needed. Document in:
- Model health log
- Weekly model review (see governance checklist)
- If preparing to retrain: heads-up to ML team

---

### Scenario 4: "Model producing biased outputs"

**Detection:** Fairness monitoring alert, customer complaint, internal audit finding, or regulatory inquiry.

#### CRITICAL: This is a compliance incident. Treat with urgency regardless of technical severity.

#### Triage Steps

```
1. CONFIRM bias
   - Review fairness metrics across protected classes
   - Is the disparity statistically significant?
   - What's the affected population size?
   - Compare current metrics to approved thresholds

2. ASSESS regulatory exposure
   - Which regulations apply? (SR 11-7, GDPR Art. 22, EBA, local laws)
   - Are affected decisions reversible? (loan denials vs recommendations)
   - Has the bias existed since deployment or is it new?
   - Are there customer complaints on record?

3. IMMEDIATE RESPONSE
   ┌─────────────────────────────────────────────────────────────────┐
   │ If bias is confirmed AND affects protected classes:             │
   │                                                                 │
   │   a. Notify compliance/legal IMMEDIATELY                       │
   │   b. Document everything from this point                       │
   │   c. Consider: suspend model or switch to rule-based fallback  │
   │   d. Do NOT retrain without compliance approval                │
   │   e. Preserve all evidence (model version, data, predictions)  │
   │                                                                 │
   │ If bias is borderline or in non-regulated context:             │
   │                                                                 │
   │   a. Notify ML team lead and compliance                        │
   │   b. Investigate root cause in training data                   │
   │   c. Prepare remediation options                               │
   │   d. Schedule review within 24 hours                           │
   └─────────────────────────────────────────────────────────────────┘

4. ROOT CAUSE INVESTIGATION
   - Training data bias: was the training data representative?
   - Feature proxies: are features acting as proxies for protected attributes?
   - Concept drift: has the model's behavior changed since approval?
   - Evaluation gap: was the bias present at deployment but not caught?

5. REMEDIATION (requires compliance approval)
   - Retrain with debiased data
   - Add fairness constraints to training objective
   - Remove proxy features
   - Switch to interpretable model for this use case
   - Implement post-processing fairness adjustments

6. DOCUMENTATION (regulatory-grade)
   - Complete timeline from detection to resolution
   - Root cause analysis
   - Impact assessment (how many decisions affected)
   - Remediation steps taken
   - Controls added to prevent recurrence
   - Independent validation of remediated model
```

#### Escalation

| Action | Timeline | Who |
|--------|---------|-----|
| Initial notification to compliance | Immediately on confirmation | Compliance officer |
| Model suspension decision | Within 1 hour | Compliance + business owner |
| Regulatory notification (if required) | Per regulatory timeline | Legal + compliance |
| Root cause report | Within 48 hours | ML team + compliance |
| Remediation plan | Within 1 week | Cross-functional team |
| Remediated model deployed | Per governance process | Full approval chain |

---

### Scenario 5: "Retraining pipeline failed"

**Detection:** Pipeline orchestrator alert, scheduled job failure notification.

#### Triage Steps

```
1. ASSESS urgency
   - When was the model last successfully retrained?
   - How old is the currently serving model?
   - Is there any drift or accuracy degradation with the current model?
   - Is this a one-time failure or recurring?

2. DIAGNOSE failure
   Which stage failed?
   
   ┌────────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
   │  Data ingestion│     │   Training    │     │  Evaluation  │     │ Registration │
   │    failed      │     │    failed     │     │   failed     │     │    failed    │
   └───────┬────────┘     └───────┬───────┘     └──────┬───────┘     └──────┬───────┘
           │                      │                     │                     │
           ▼                      ▼                     ▼                     ▼
    - Source unavail       - OOM error            - Metrics below       - Registry down
    - Schema changed       - Dependency fail        threshold           - Auth expired
    - Auth expired         - GPU unavailable      - Eval data issue     - Quota exceeded
    - Network timeout      - Code bug             - Metric calc error   - Network issue
    - Data too large       - Config error         - Threshold wrong     - Version conflict

3. RESPOND based on failure stage
   
   Data ingestion failed:
     → Check upstream source, fix connection/auth, retry
     → If source is gone/changed: escalate to data team
   
   Training failed:
     → Transient (OOM, GPU): retry with adjusted resources
     → Code/dependency: rollback to last working code version, fix forward
     → Config: check recent config changes
   
   Evaluation failed (metrics below threshold):
     → Check: is the threshold correct? Was training data quality good?
     → This might be correct behavior (bad model = don't deploy it)
     → Investigate: why did training produce a worse model?
   
   Registration failed:
     → Usually infra: retry, check permissions, check registry health

4. VERIFY
   - Re-run pipeline after fix
   - Confirm new model meets evaluation criteria
   - Check model is correctly registered and available for serving
   - If time-sensitive: manually promote last good model version as interim
```

#### Key principle: A failed retraining pipeline is NOT immediately urgent if:
- The currently serving model is still performing within SLO
- The model is not so old that it violates compliance requirements
- There's no active drift that necessitates immediate retraining

---

## Escalation Matrix

| Incident type | First responder | Escalation L1 | Escalation L2 | Escalation L3 |
|---------------|----------------|---------------|---------------|---------------|
| **Serving errors** | MLOps on-call | Platform lead | ML team lead | Engineering director |
| **Accuracy drop** | MLOps on-call | ML team lead | Data science lead | Business stakeholder |
| **Data quality** | Data platform on-call | Data engineering lead | Data science lead | Platform lead |
| **Drift** | MLOps on-call | ML team lead | Data science lead | (usually resolves at L1) |
| **Pipeline failure** | MLOps on-call | Platform lead | ML team lead | (usually resolves at L1) |
| **Bias/fairness** | MLOps on-call | Compliance officer | Legal + business owner | Executive sponsor |

### Contact Template

| Role | Name | Contact | Availability |
|------|------|---------|-------------|
| MLOps on-call | _(fill in)_ | _(Slack/phone)_ | 24/7 rotation |
| ML team lead | _(fill in)_ | _(Slack/phone)_ | Business hours + pager |
| Data engineering lead | _(fill in)_ | _(Slack/phone)_ | Business hours + pager |
| Compliance officer | _(fill in)_ | _(Slack/phone)_ | Business hours (phone for P1) |
| Business stakeholder | _(fill in)_ | _(Slack/email)_ | Business hours |

---

## Communication Templates

### Template 1: Initial Incident Notification (Internal)

```
🔴 ML INCIDENT — [P1/P2/P3/P4] — [Incident Type]

Summary: [One sentence: what happened]
Impact: [Who/what is affected, how many predictions]
Status: Investigating / Mitigating / Resolved
Current model: [model name, version]
Detection time: [when alert fired]
Response started: [when triage began]

Next update in: [30 min / 1 hour / etc.]
Incident channel: #incident-[name]
```

### Template 2: Stakeholder Update (Business)

```
Subject: ML Model [Name] — Performance Incident Update

Current status: [Investigating / Mitigating / Resolved]

What happened:
[2-3 sentences in business language, no jargon]

Business impact:
- [X predictions affected since Y time]
- [Business metric impact, if known]
- [Customer-facing impact, if any]

What we're doing:
- [Current action being taken]
- [Expected resolution time]

What you need to do:
- [Any actions needed from business team, or "No action required"]

Next update: [time]
Contact: [incident lead name and channel]
```

### Template 3: Resolution Notification

```
✅ ML INCIDENT RESOLVED — [Incident Type]

Summary: [One sentence: what happened and how it was fixed]
Duration: [start time] to [end time] ([X hours/minutes])
Impact: [Total predictions affected, business impact]
Resolution: [What fixed it: rollback / retrain / data fix / config change]
Current model: [model name, version now serving]

Postmortem scheduled: [date/time]
Postmortem doc: [link to ml-postmortem-template.md instance]

Follow-up actions in progress:
- [Action 1]
- [Action 2]
```

### Template 4: Compliance/Regulatory Notification (Bias Incident)

```
Subject: Model Fairness Incident — [Model Name] — [Date]

Classification: [Potential regulatory impact / Internal finding]

Summary:
[Brief factual description of the finding]

Affected model:
- Name: [model name]
- Version: [version]
- Purpose: [what it does]
- In production since: [date]

Finding:
- Metric: [which fairness metric]
- Threshold: [approved threshold]
- Current value: [observed value]
- Affected group: [protected class]
- Estimated affected decisions: [number]

Immediate actions taken:
- [Model suspended / fallback activated / monitoring enhanced]
- [Evidence preserved]
- [Investigation initiated]

Requested actions:
- [Compliance review and guidance]
- [Determination of regulatory notification requirements]

Timeline for root cause analysis: [target date]
Point of contact: [name, role]
```

---

## Post-Incident Actions

After every P1 or P2 incident:
1. **Postmortem** within 5 business days (use `ml-postmortem-template.md`)
2. **Action items** assigned with owners and due dates
3. **Monitoring gap** identified and addressed (why didn't we catch this sooner?)
4. **Runbook update** — did this runbook help? What was missing?
5. **Governance review** — do approval gates need updating?

After every bias/fairness incident:
1. All of the above, PLUS:
2. **Compliance sign-off** on resolution
3. **Independent validation** of remediated model
4. **Documentation package** for regulatory file
5. **Process improvement** — how to prevent this category of bias

---

## Appendix: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                   ML INCIDENT QUICK REFERENCE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CONFIRM — Is the alert real? Check dashboard.           │
│  2. CLASSIFY — What type? What severity?                    │
│  3. COMMUNICATE — Post in incident channel.                 │
│  4. CONTAIN — Rollback if user-facing. Preserve evidence.   │
│  5. DIAGNOSE — Data? Drift? Code? Config? External?         │
│  6. RESOLVE — Fix data / Retrain / Rollback / Escalate.     │
│  7. VERIFY — Is the fix working? Metrics recovering?        │
│  8. DOCUMENT — Timeline, root cause, action items.          │
│  9. POSTMORTEM — Schedule within 5 days.                    │
│                                                             │
│  When in doubt: rollback to last known good model version.  │
│  When in regulatory doubt: escalate to compliance first.    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
