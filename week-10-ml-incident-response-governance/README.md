# Week 10 — ML Incident Response & Governance

**Time budget:** 8–10 hours  
**Goal:** Build a complete ML incident response framework, postmortem template, and governance checklist — artifacts you could pitch to use at CloudFactory tomorrow.  
**Key insight:** This is where your banking/regulatory background becomes a **DIFFERENTIATOR**, not a gap. You already know incident governance, compliance, and audit. Now you're extending those frameworks to cover ML-specific failure modes.

---

## Why This Week Matters

Pure ML engineers often build brilliant models with no incident playbook, no governance trail, and no compliance documentation. They've never written a runbook or sat through a regulatory audit.

**You have.** This week you're combining:
- Your incident response instincts (triage, escalation, communication)
- Your regulatory compliance experience (audit trails, documentation, approvals)
- Your blameless postmortem practice (root cause, action items, follow-ups)
- Your governance frameworks (gates, sign-offs, lifecycle management)

...with the ML-specific failure modes you've learned over the past 9 weeks (drift, data quality, pipeline failures, serving errors).

The result: portfolio-quality governance artifacts that demonstrate exactly the kind of operational maturity ML teams are missing.

---

## Concepts to Cover

### 1. ML Incident Categories (Classification)

ML systems fail differently from traditional services. Here's your incident taxonomy:

| Category | What it means | Detection method | Urgency |
|----------|--------------|-----------------|---------|
| **Drift incidents** | Model's input distribution or concept has shifted; predictions degrading | Statistical tests, monitoring dashboards | Medium-High (silent degradation) |
| **Data quality incidents** | Upstream data is corrupted, stale, missing, or schema-broken | Data validation checks, pipeline alerts | High (garbage in → garbage out) |
| **Pipeline failures** | Training or feature pipelines fail to complete | Orchestrator alerts, job failures | Medium (no new model, old one still serving) |
| **Serving errors** | Model endpoint returning errors, high latency, or unavailable | Standard ops monitoring (HTTP 5xx, latency) | Critical (user-facing) |
| **Training failures** | Model training produces poor results or fails to converge | Evaluation metrics, training logs | Low-Medium (no immediate prod impact) |
| **Bias/fairness incidents** | Model producing discriminatory or unfair outputs | Fairness monitoring, compliance audits | Critical (regulatory + reputational) |

#### The Silent Failure Problem

The critical difference from traditional ops: **ML failures are often silent**. Your service returns HTTP 200, latency is normal, no errors in logs — but the model is confidently making terrible predictions.

```
Traditional service failure:        ML failure:
┌──────────────────────┐            ┌──────────────────────┐
│  Request comes in    │            │  Request comes in    │
│  Service crashes     │            │  Model responds 200  │
│  HTTP 500 returned   │            │  Prediction is wrong │
│  Alert fires         │            │  No alert fires      │
│  Incident opened     │            │  Customer churns     │
│  Engineer fixes      │            │  Nobody knows yet    │
└──────────────────────┘            └──────────────────────┘
```

This is why ML monitoring (Weeks 8–9) and governance (this week) are inseparable.

### 2. The Retraining Decision Tree

When something goes wrong with a model, the response isn't always "retrain." Here's the decision framework:

```
Model performance degraded
         │
         ▼
┌─────────────────────────────┐
│ Is the model serving errors │──Yes──▶ ROLLBACK immediately
│ (500s, timeouts, crashes)?  │         (operational failure)
└─────────────────────────────┘
         │ No
         ▼
┌─────────────────────────────┐
│ Is incoming data quality    │──Yes──▶ FIX DATA first
│ degraded? (nulls, schema   │         (don't retrain on garbage)
│ breaks, stale features)    │
└─────────────────────────────┘
         │ No
         ▼
┌─────────────────────────────┐
│ Is this concept drift?      │──Yes──▶ RETRAIN on recent data
│ (the world changed, model  │         (model needs to learn
│ assumptions are outdated)  │          new patterns)
└─────────────────────────────┘
         │ No
         ▼
┌─────────────────────────────┐
│ Is this data drift without  │──Yes──▶ INVESTIGATE
│ accuracy impact yet?        │         (monitor closely,
│                             │          prepare to retrain)
└─────────────────────────────┘
         │ No
         ▼
┌─────────────────────────────┐
│ Is this a one-time anomaly? │──Yes──▶ DOCUMENT & MONITOR
│ (holiday, outage, etc.)    │         (no action needed yet)
└─────────────────────────────┘
         │ No
         ▼
    ESCALATE to ML team
    for deeper investigation
```

See `retraining-decision-tree.md` for the full version with timing guidelines and risk assessment.

### 3. Blameless Postmortems for ML Incidents

You already know blameless postmortems. ML-specific additions:

| Standard section | ML-specific addition |
|-----------------|---------------------|
| **Timeline** | Include when drift was first detectable vs when it was detected (detection lag) |
| **Root cause** | Categorize: drift, data quality, pipeline, code bug, config error |
| **Impact** | Quantify: how many predictions were affected, business impact of wrong predictions |
| **Resolution** | Document: retrain vs rollback vs data fix decision and rationale |
| **Action items** | Add: monitoring gaps, retraining trigger improvements, data validation additions |

New sections for ML postmortems:
- **Model version info** — which model was serving, what it was trained on
- **Drift analysis** — statistical evidence of drift, when it started
- **Data lineage** — what data fed the model, was it correct
- **Retraining decision rationale** — why you chose retrain/rollback/fix-data

See `ml-postmortem-template.md` for the complete template.

### 4. Model Governance: Lineage, Audit, Reproducibility

Governance for ML means answering: **"For any prediction this model made, can you explain how the model was built, what data it used, and who approved it?"**

#### Model Lineage Tracking

```
Data Source → Data Version → Feature Pipeline → Training Pipeline → Model Version → Deployment
     │              │               │                    │                │             │
     ▼              ▼               ▼                    ▼                ▼             ▼
  Who owns it?  What changed?  What transforms?   What params?     Who approved?  What SLOs?
```

Every model in production needs:
- **Data lineage** — which datasets, which versions, what preprocessing
- **Code lineage** — which training code, which commit, which pipeline version
- **Experiment lineage** — which experiments led to this model, what was tried and rejected
- **Approval lineage** — who approved promotion to production, when, based on what evidence

#### Reproducibility Requirements

A model deployment must be reproducible. Given the same:
- Data version
- Code version
- Configuration
- Random seeds
- Environment (pinned dependencies)

...you must be able to produce the same (or statistically equivalent) model.

**Why banking cares:** Regulators may ask "why did this model deny this customer's loan?" — you need to reproduce the exact model state at that point in time.

#### Audit Trail

Every model action is logged:
| Event | What to log |
|-------|-------------|
| Training started | Who triggered, what data, what config |
| Evaluation complete | All metrics, pass/fail on gates |
| Model registered | Version, metrics, who registered |
| Approval granted | Who approved, evidence reviewed |
| Deployment | When, where, by whom, canary results |
| Rollback | Why, who decided, what replaced it |
| Retirement | When, why, what replaced it |

### 5. Regulatory Considerations (Your Banking Edge)

This section is where you are miles ahead of most ML engineers. They build models; you know how to govern them in a regulated environment.

#### Model Explainability

Regulators want to know **why** a model made a decision. Requirements vary by jurisdiction:
- **SR 11-7 (US Federal Reserve)** — model risk management guidance
- **GDPR Article 22 (EU)** — right to explanation for automated decisions
- **EBA Guidelines (EU Banking Authority)** — IRB model validation

Tools for explainability:
- **SHAP** — SHapley Additive exPlanations (feature importance per prediction)
- **LIME** — Local Interpretable Model-agnostic Explanations
- **Model cards** — standardized documentation of model behavior and limitations

#### Bias Monitoring

Models trained on historical data inherit historical biases. In banking:
- Loan approval models may discriminate by race, gender, age, postcode
- Fraud detection may have higher false-positive rates for certain demographics
- Credit scoring may perpetuate historical lending disparities

**Monitoring requirements:**
- Track prediction distributions across protected classes
- Monitor false positive/negative rates by demographic group
- Set thresholds for acceptable disparate impact ratios
- Regular fairness audits (quarterly minimum in most jurisdictions)

#### Documentation Requirements

Every model in production needs:
1. **Model card** — purpose, performance, limitations, intended use
2. **Data sheet** — data sources, collection methods, known biases
3. **Validation report** — independent evaluation of model performance
4. **Monitoring plan** — what's monitored, thresholds, response procedures
5. **Change log** — every modification to the model or its inputs

### 6. Model Lifecycle Governance

```
┌─────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
│  Build  │───▶│   Validate  │───▶│  Approve │───▶│   Deploy    │───▶│  Monitor │
│         │    │             │    │          │    │             │    │          │
└─────────┘    └─────────────┘    └──────────┘    └─────────────┘    └──────────┘
                                        │                                   │
                                   Gate: Who                           Trigger:
                                   signs off?                          Retrain/
                                   What evidence?                      Retire
```

#### Approval Gates

| Gate | Requirement | Who approves |
|------|------------|--------------|
| **Evaluation gate** | Model meets accuracy/precision/recall thresholds | Automated (pipeline) |
| **Bias/fairness gate** | No disparate impact above threshold | Compliance team |
| **Documentation gate** | Model card, data sheet, monitoring plan complete | Model risk team |
| **Security gate** | No PII leakage, adversarial robustness tested | Security team |
| **Business gate** | Expected business impact validated | Business stakeholder |
| **Deployment gate** | Canary successful, rollback plan documented | Platform/MLOps team (you) |

#### Rollback SLAs

| Incident type | Rollback SLA | Rationale |
|---------------|-------------|-----------|
| Model serving errors (5xx) | < 5 minutes | User-facing, automated rollback |
| Bias/fairness violation detected | < 1 hour | Regulatory exposure, manual review |
| Significant accuracy degradation | < 4 hours | Business impact, needs investigation |
| Drift detected, no accuracy drop | No rollback needed | Monitor and schedule retrain |
| Data quality issue (stale data) | < 2 hours | Fix data pipeline, rollback if severe |

See `model-governance-checklist.md` for the complete operational checklist.

---

## Hands-on Lab

This week is primarily **documentation and process work** — which is exactly what a support lead produces. Your deliverables are:

### 1. ML Incident Runbook
Review and customize `ml-incident-runbook.md` for your context. This is a portfolio piece.

### 2. Postmortem Template
Review `ml-postmortem-template.md`. Practice by writing a mock postmortem for:
> "Our fraud detection model's precision dropped from 0.92 to 0.78 over two weeks. We didn't detect it until a customer complaint spike."

### 3. Governance Checklist
Review `model-governance-checklist.md`. Consider: how would you adapt this for CloudFactory's environment?

### 4. Retraining Decision Tree
Walk through `retraining-decision-tree.md` with a scenario:
> "Drift monitoring shows feature distribution shift in 3 of 12 features. Model accuracy is still within SLO. What do you do?"

---

## Key Takeaways for Your Role

1. **You already know 70% of this.** Incident response, postmortems, governance, compliance — you've done this for years. The ML layer is just new failure modes.

2. **ML teams need you.** Most ML engineers can build models but can't write a runbook, define escalation paths, or satisfy a regulator. That's your value.

3. **Silent failures are the new frontier.** Traditional monitoring catches crashes. ML monitoring catches degradation. You need both layers.

4. **The retraining decision isn't always "retrain."** Sometimes it's rollback, fix data, or just monitor. The decision tree is your playbook.

5. **Governance is a competitive advantage.** Companies that can explain, audit, and reproduce their models can operate in regulated industries. Companies that can't, can't.

---

## Connecting to Your Background

| Your banking experience | Week 10 ML equivalent |
|------------------------|----------------------|
| Incident response runbooks | ML incident runbook (new failure modes) |
| Blameless postmortems | ML postmortems (drift analysis, model version info) |
| Change advisory boards | Model approval gates |
| Audit trails for compliance | Model lineage tracking |
| Regulatory documentation | Model cards, data sheets |
| Rollback procedures | Model version rollback + retraining decisions |
| Escalation matrices | ML-specific escalation (data team, ML team, compliance) |
| SLA definitions | Rollback SLAs per incident type |

---

## Resources

- 📚 [Google — ML Model Risk Management](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) — governance patterns
- 📚 [Responsible AI Practices (Google)](https://ai.google/responsibility/responsible-ai-practices/) — fairness and accountability
- 📚 [Model Cards for Model Reporting (Mitchell et al.)](https://arxiv.org/abs/1810.03993) — the original paper
- 📚 [Datasheets for Datasets (Gebru et al.)](https://arxiv.org/abs/1803.09010) — data documentation standard
- 📚 [SR 11-7: Guidance on Model Risk Management (Federal Reserve)](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) — US banking model governance
- 📚 [SHAP Documentation](https://shap.readthedocs.io/) — model explainability
- 📚 [Evidently AI — ML Monitoring](https://www.evidentlyai.com/) — drift and fairness monitoring
- 📚 [Chip Huyen — Designing ML Systems, Ch. 11](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) — infrastructure and governance

---

## Checklist

- [ ] Read through all concepts above
- [ ] Review `ml-incident-runbook.md` — customize for your mental model
- [ ] Review `ml-postmortem-template.md` — write a mock postmortem for the fraud model scenario
- [ ] Review `model-governance-checklist.md` — identify which gates your current bank already has
- [ ] Walk through `retraining-decision-tree.md` with 2–3 scenarios
- [ ] Write a 1-page "ML Governance Proposal" as if pitching it to CloudFactory leadership
- [ ] Identify 3 things your banking background gives you that pure ML engineers lack
- [ ] Add these artifacts to your portfolio repo — they demonstrate operational maturity

**Milestone 3 deliverable:** A complete ML on-call runbook + SLO definitions (from Week 9) + postmortem template + governance checklist. This is portfolio-grade work.
