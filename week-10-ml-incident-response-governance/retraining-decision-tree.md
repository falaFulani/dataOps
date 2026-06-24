# Retraining Decision Tree

**Purpose:** A structured decision framework for responding to model performance issues. Not every problem is solved by retraining — this tree helps you choose the right response and understand the risks of each path.

**When to use:** Whenever monitoring flags a potential model issue (drift, accuracy drop, data quality, etc.)

---

## The Decision Tree

```
╔══════════════════════════════════════════════════════════════════════════╗
║                     MODEL ISSUE DETECTED                                 ║
║                                                                          ║
║  Entry point: Alert fires, metric breaches threshold, or manual report   ║
╚══════════════════════════════════════════════════════════╦═══════════════╝
                                                          ║
                                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │  STEP 1: Is the model serving operational errors? │
                    │  (HTTP 5xx, timeouts, crashes, OOM)              │
                    └───────────────────────┬─────────────────────────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │ YES             │                  │ NO
                          ▼                 │                  ▼
              ┌───────────────────┐         │    ┌─────────────────────────────┐
              │ ⚡ ROLLBACK NOW   │         │    │  STEP 2: Is data quality    │
              │                   │         │    │  degraded?                   │
              │ Target: < 5 min   │         │    │  (nulls, stale, schema      │
              │ Action: Revert to │         │    │   break, missing features)   │
              │ last good version │         │    └──────────────┬──────────────┘
              │ Then: investigate │         │                   │
              └───────────────────┘         │     ┌────────────┼────────────┐
                                            │     │ YES        │            │ NO
                                            │     ▼            │            ▼
                                            │ ┌──────────────────┐  ┌─────────────────────────┐
                                            │ │ 🔧 FIX DATA      │  │  STEP 3: Is this         │
                                            │ │                  │  │  concept drift?           │
                                            │ │ Target: < 2 hrs  │  │  (world changed, model   │
                                            │ │ Action: Fix the  │  │   assumptions outdated)   │
                                            │ │ upstream pipeline │  └────────────┬────────────┘
                                            │ │ Do NOT retrain   │               │
                                            │ │ on corrupted data│     ┌────────┼────────┐
                                            │ └──────────────────┘     │ YES    │        │ NO
                                            │                          ▼        │        ▼
                                            │              ┌──────────────────┐  │  ┌─────────────────────────┐
                                            │              │ 🔄 RETRAIN       │  │  │  STEP 4: Is there data   │
                                            │              │                  │  │  │  drift WITHOUT accuracy   │
                                            │              │ Target: < 4 hrs  │  │  │  impact?                  │
                                            │              │ Action: Retrain  │  │  └────────────┬────────────┘
                                            │              │ on recent data   │  │               │
                                            │              │ that reflects    │  │     ┌────────┼────────┐
                                            │              │ new reality      │  │     │ YES    │        │ NO
                                            │              └──────────────────┘  │     ▼        │        ▼
                                            │                                    │ ┌──────────────┐ ┌──────────────────┐
                                            │                                    │ │ 👀 MONITOR   │ │  STEP 5: Is this │
                                            │                                    │ │              │ │  a one-time      │
                                            │                                    │ │ Target: N/A  │ │  anomaly?        │
                                            │                                    │ │ Action: Watch│ │  (holiday, event,│
                                            │                                    │ │ closely, prep│ │   outage)        │
                                            │                                    │ │ retrain if   │ └────────┬─────────┘
                                            │                                    │ │ accuracy     │          │
                                            │                                    │ │ drops        │  ┌───────┼───────┐
                                            │                                    │ └──────────────┘  │ YES   │       │ NO
                                            │                                    │                   ▼       │       ▼
                                            │                                    │       ┌──────────────┐  ┌──────────────┐
                                            │                                    │       │ 📝 DOCUMENT  │  │ ⬆️ ESCALATE  │
                                            │                                    │       │              │  │              │
                                            │                                    │       │ Action: Log  │  │ Action: Get  │
                                            │                                    │       │ the anomaly, │  │ ML team to   │
                                            │                                    │       │ no action    │  │ investigate  │
                                            │                                    │       │ required yet │  │ deeper       │
                                            │                                    │       └──────────────┘  └──────────────┘
```

---

## Decision Paths: Detailed Guidance

### Path 1: ⚡ ROLLBACK NOW

**When:** Model endpoint is returning errors, crashing, timing out, or completely unavailable.

| Aspect | Details |
|--------|---------|
| **Target response time** | < 5 minutes |
| **Trigger** | HTTP 5xx > threshold, latency > 5x normal, OOM kills, pod crashes |
| **Action** | Revert to previous model version (automated if possible) |
| **Who decides** | On-call engineer (pre-authorized, no approval needed) |
| **Risk of action** | Low — reverting to a known-good version is safe |
| **Risk of inaction** | High — users are impacted RIGHT NOW |
| **After rollback** | Investigate root cause at normal pace |

**Automation opportunity:** Configure automatic rollback when health checks fail for > 60 seconds.

**Questions to answer after rollback:**
- What changed? (deployment, config, dependency, infrastructure?)
- Was the new model version ever properly tested?
- Did evaluation gates pass? If so, why did it fail in production?
- Is this a reproducible failure or transient?

---

### Path 2: 🔧 FIX DATA

**When:** Upstream data is corrupted, stale, missing fields, or has schema breaks. The model itself is fine — it's being fed garbage.

| Aspect | Details |
|--------|---------|
| **Target response time** | < 2 hours for fix; consider model rollback if data can't be fixed quickly |
| **Trigger** | Data quality alerts, null spikes, schema validation failures, freshness alerts |
| **Action** | Fix the data pipeline; do NOT retrain on corrupted data |
| **Who decides** | MLOps on-call + data engineering |
| **Risk of action** | Low — fixing data is always correct |
| **Risk of inaction** | High — model predictions degrade with bad input |
| **Critical rule** | NEVER retrain on corrupted data. Fix the source first. |

**Decision sub-tree for data issues:**

```
Data quality issue confirmed
         │
         ▼
┌─────────────────────────────────┐
│ Is the model still serving      │──Yes──▶ Is it using stale/corrupt features?
│ predictions?                    │              │
└─────────────────────────────────┘              ├── Yes + accuracy degraded → 
         │ No (pipeline failure)                 │     Rollback model OR serve
         │                                       │     fallback while fixing data
         ▼                                       │
   Fix pipeline.                                 ├── Yes + accuracy still OK → 
   Model serving old                             │     Fix data pipeline, monitor
   (last good) version.                          │     model closely
   Less urgent.                                  │
                                                 └── No (model has fallback logic) →
                                                       Fix data pipeline, low urgency
```

**Questions to answer:**
- Where did the data break? (source system, ETL, feature pipeline, feature store)
- How long has the data been bad? (affects impact assessment)
- Do we need to backfill any data?
- Should we add a data quality gate that would have caught this?

---

### Path 3: 🔄 RETRAIN

**When:** The world has genuinely changed (concept drift). The model's learned patterns no longer match reality. New data reflects a new truth the model needs to learn.

| Aspect | Details |
|--------|---------|
| **Target response time** | < 4 hours for the decision; retraining itself may take longer |
| **Trigger** | Concept drift confirmed, accuracy degradation with clean data, known world change |
| **Action** | Retrain on recent data that reflects the new reality |
| **Who decides** | ML team lead (standard); MLOps lead can authorize under expedited process |
| **Risk of action** | Medium — new model might not be better; needs evaluation gates |
| **Risk of inaction** | High — model will continue degrading if the world has truly changed |
| **Critical rule** | Always evaluate the retrained model against gates before deploying |

**Pre-retraining checklist:**

| Check | Why |
|-------|-----|
| [ ] Data quality verified | Don't retrain on bad data |
| [ ] Sufficient new labeled data available | Need ground truth for the new concept |
| [ ] Training pipeline recently tested | Don't discover pipeline bugs during an incident |
| [ ] Evaluation data reflects new reality | Old eval set may not catch new-concept performance |
| [ ] Rollback plan ready | In case retrained model is worse |
| [ ] Approval process clear | Standard or expedited? |

**Types of retraining:**

| Type | When | Data used | Risk |
|------|------|-----------|------|
| **Incremental retrain** | Gradual drift, model still OK-ish | Recent data window appended | Low (fine-tuning) |
| **Full retrain** | Significant concept shift | Entire updated dataset | Medium (model may behave differently) |
| **Architecture change** | Fundamental assumption broken | All available data | High (new model, full testing needed) |

**Questions to answer:**
- Why did the world change? (market shift, regulation, seasonality, competitor action?)
- Is this permanent or temporary? (if temporary, retraining may overfit to anomaly)
- How much recent data do we have with ground truth labels?
- Should we expand the training window or use only recent data?

---

### Path 4: 👀 MONITOR (Proactive Watch)

**When:** Drift is detected statistically but the model's accuracy hasn't dropped yet. The canary is singing but hasn't died.

| Aspect | Details |
|--------|---------|
| **Target response time** | No immediate action required; set review date |
| **Trigger** | Drift alert fires, PSI > threshold, but accuracy SLO still met |
| **Action** | Increase monitoring frequency, prepare retraining pipeline, set review date |
| **Who decides** | MLOps on-call (standard operating procedure) |
| **Risk of action** | Very low — you're just watching more carefully |
| **Risk of inaction** | Medium — drift often precedes accuracy drops; don't be caught off-guard |
| **Critical rule** | Set a specific review date. Don't just "keep an eye on it" indefinitely. |

**Monitoring escalation ladder:**

| Drift level | PSI score | Action |
|-------------|-----------|--------|
| Minor | 0.05–0.10 | Log it. Review at next weekly check. |
| Moderate | 0.10–0.20 | Daily monitoring. Prepare retraining data. Set 1-week review. |
| Significant | 0.20–0.30 | Start retraining pipeline (don't deploy yet). Set 48-hour review. |
| Severe | > 0.30 | Retrain now (Path 3). Don't wait for accuracy to drop. |

**What to prepare while monitoring:**
- [ ] Verify retraining pipeline is ready to run
- [ ] Confirm recent data is available and labeled
- [ ] Alert ML team that proactive retrain may be needed
- [ ] Check: is there a shadow model running on newer data?

---

### Path 5: 📝 DOCUMENT (One-Time Anomaly)

**When:** Metrics look weird but you've identified a known external cause that's temporary (holiday, system outage, one-time event).

| Aspect | Details |
|--------|---------|
| **Target response time** | Document within 1 business day |
| **Trigger** | Metrics anomaly + identified external cause + expectation of return to normal |
| **Action** | Document the anomaly, note expected recovery timeline, monitor |
| **Who decides** | MLOps on-call |
| **Risk of action** | Very low |
| **Risk of inaction** | Low — but undocumented anomalies cause confusion in future postmortems |
| **Critical rule** | Set a "check back" date. If metrics don't recover as expected, escalate to Path 3 or 6. |

**Document in model health log:**
- Date and duration of anomaly
- External cause identified
- Evidence supporting "this is temporary"
- Expected recovery date
- What to do if it doesn't recover by that date

---

### Path 6: ⬆️ ESCALATE

**When:** You've ruled out the obvious causes and don't have a clear diagnosis. Something is wrong but it doesn't fit the standard categories.

| Aspect | Details |
|--------|---------|
| **Target response time** | Escalate within 1 hour of ruling out standard causes |
| **Trigger** | Unknown root cause after initial triage |
| **Action** | Bring in ML team / data science for deeper investigation |
| **Who decides** | MLOps on-call (escalation doesn't require approval) |
| **Risk of action** | Low — you're getting more eyes on the problem |
| **Risk of inaction** | Unknown — that's the point; you can't assess risk without diagnosis |
| **Critical rule** | Don't spin for hours trying to solve something outside your expertise |

**When to escalate vs keep investigating:**
- Escalate if: root cause unclear after 30 minutes of triage
- Escalate if: multiple failure signals that don't fit one category
- Escalate if: model is in a regulated domain and you're unsure of compliance implications
- Keep investigating if: you have a strong hypothesis and are making progress

---

## Timing Summary

| Path | Response target | Resolution target | Urgency driver |
|------|----------------|-------------------|----------------|
| ⚡ Rollback | < 5 minutes | Minutes (rollback is the fix) | Users impacted now |
| 🔧 Fix Data | < 2 hours | Hours to days (depends on pipeline) | Garbage predictions |
| 🔄 Retrain | < 4 hours (decision) | Hours to days (training + gates) | Accuracy degrading |
| 👀 Monitor | Same day (acknowledge) | Days to weeks (watch + prepare) | Prevent future impact |
| 📝 Document | Within 1 business day | N/A (no fix needed) | Knowledge management |
| ⬆️ Escalate | < 1 hour | Depends on investigation | Unknown risk |

---

## Risk Assessment Matrix

| Path | Risk of taking action | Risk of NOT taking action | Reversibility |
|------|----------------------|--------------------------|---------------|
| ⚡ Rollback | Low (known-good version) | Critical (ongoing user impact) | Fully reversible |
| 🔧 Fix Data | Low (fixing source of truth) | High (predictions degrade) | Fully reversible |
| 🔄 Retrain | Medium (new model may differ) | High (ongoing degradation) | Reversible (rollback new model) |
| 👀 Monitor | Very low (just watching) | Medium (may miss window to act) | N/A |
| 📝 Document | None | Low (confusion later) | N/A |
| ⬆️ Escalate | Low (more eyes = better) | Unknown (that's the problem) | N/A |

---

## Common Mistakes

| Mistake | Why it's wrong | Better approach |
|---------|---------------|----------------|
| Retrain on corrupted data | Model learns the corruption | Fix data first, then retrain if needed |
| Retrain on a one-time anomaly | Model overfits to the anomaly | Document and wait for things to normalize |
| Wait too long when drift is accelerating | Accuracy collapse is harder to recover from | Set aggressive review dates, act proactively |
| Rollback when the world genuinely changed | Old model is wrong for the new reality too | The old model will also be wrong — retrain |
| Skip evaluation gates during emergency retrain | Might deploy a worse model | Always run gates, even on expedited timeline |
| Investigate alone for hours | Some problems need specialized knowledge | Escalate after 30 minutes of no progress |

---

## Integration with Governance

Every decision on this tree generates governance artifacts:

| Decision | Governance requirement |
|----------|----------------------|
| Rollback | Log in audit trail: reason, who decided, versions involved |
| Fix data | Document root cause, add data quality check to prevent recurrence |
| Retrain | Follow expedited or standard approval process (see governance checklist) |
| Monitor | Log in model health record, set review date |
| Document | Add to model health log and weekly review |
| Escalate | Update incident record with escalation path and outcome |

---

## Practice Scenarios

Use these to walk through the decision tree:

1. **"Fraud model precision dropped from 0.92 to 0.85 overnight. No code changes deployed."**
   → Expected path: Step 2 (check data) → Step 3 (concept drift likely if data is clean) → Retrain

2. **"Recommendation model returning 500 errors for 20% of requests since last deployment."**
   → Expected path: Step 1 → Rollback immediately

3. **"Credit scoring model shows PSI of 0.15 on income feature. Accuracy unchanged."**
   → Expected path: Steps 1-3 all No → Step 4 → Monitor

4. **"Customer churn model accuracy dropped 30%. Upstream data pipeline was down for 12 hours yesterday."**
   → Expected path: Step 2 → Fix data (backfill missing data, then reassess)

5. **"Loan approval model shows 2x denial rate for a specific demographic group."**
   → This bypasses the tree entirely → Bias incident → See runbook Scenario 4
