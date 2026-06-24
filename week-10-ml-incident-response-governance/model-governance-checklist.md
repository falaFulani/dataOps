# Model Governance Checklist

**Purpose:** Operational checklist for governing ML model deployments throughout their lifecycle. Covers pre-deployment gates, approval process, post-deployment monitoring, regular reviews, compliance documentation, and audit requirements.

**Who uses this:** ML Support Lead, Platform/MLOps team, Model Risk team, Compliance team.

**When to use:** Every model deployment (new or retrained), monthly reviews, and audit preparations.

---

## 1. Pre-Deployment Gates

Every model must pass ALL gates before production deployment. A single gate failure blocks deployment until resolved.

### 1.1 Evaluation Metrics Gate

| Check | Requirement | Status |
|-------|------------|--------|
| [ ] Accuracy/F1/AUC meets threshold | ≥ [defined threshold per model] | |
| [ ] Performance on holdout test set | No significant degradation from baseline | |
| [ ] Performance on edge cases | Known edge cases tested and documented | |
| [ ] Performance across segments | No segment performs below minimum threshold | |
| [ ] Comparison to current production model | New model ≥ current model (or justified exception) | |
| [ ] Latency requirements met | p50 < [X]ms, p99 < [Y]ms | |
| [ ] Throughput requirements met | Handles expected QPS with headroom | |
| [ ] Resource requirements acceptable | Memory/CPU within allocated limits | |

**Gate owner:** ML team (automated in pipeline)  
**Override authority:** ML team lead + documented justification

### 1.2 Bias and Fairness Gate

| Check | Requirement | Status |
|-------|------------|--------|
| [ ] Demographic parity assessed | Prediction rates across protected classes within threshold | |
| [ ] Equal opportunity assessed | True positive rates across groups within threshold | |
| [ ] Disparate impact ratio | ≥ 0.8 (four-fifths rule) or jurisdiction-specific threshold | |
| [ ] False positive rate parity | FPR difference across groups < [threshold] | |
| [ ] Proxy feature analysis | No features serving as proxies for protected attributes | |
| [ ] Historical bias check | Training data assessed for historical bias patterns | |
| [ ] Intersectional analysis | Checked across intersections of protected classes | |

**Gate owner:** Compliance team + ML team  
**Override authority:** Chief Risk Officer (with documented justification and remediation plan)  
**Tools:** Fairlearn, AIF360, Evidently, or custom fairness metrics

### 1.3 Documentation Gate

| Check | Requirement | Status |
|-------|------------|--------|
| [ ] Model card complete | All sections filled, reviewed by peer | |
| [ ] Data sheet complete | Data sources, collection methods, known limitations | |
| [ ] Monitoring plan defined | What metrics, what thresholds, what alerts | |
| [ ] Runbook entry created | Incident response steps for this model | |
| [ ] Rollback plan documented | How to rollback, who decides, what triggers it | |
| [ ] Change log updated | What changed from previous version | |
| [ ] Training reproducibility documented | Data version, code commit, config, environment | |

**Gate owner:** ML team lead  
**Override authority:** None — documentation is non-negotiable for regulated models

### 1.4 Security Gate

| Check | Requirement | Status |
|-------|------------|--------|
| [ ] No PII in model artifacts | Model doesn't memorize or leak training PII | |
| [ ] Input validation defined | Model handles malformed/adversarial inputs gracefully | |
| [ ] Adversarial robustness tested | Tested against known attack vectors (if applicable) | |
| [ ] Access controls defined | Who can invoke, who can update, who can view predictions | |
| [ ] Encryption requirements met | Data in transit and at rest encrypted | |
| [ ] Dependency scan passed | No known vulnerabilities in model dependencies | |

**Gate owner:** Security team  
**Override authority:** CISO (with risk acceptance document)

### 1.5 Business Validation Gate

| Check | Requirement | Status |
|-------|------------|--------|
| [ ] Business stakeholder reviewed | Predictions make business sense on sample data | |
| [ ] Expected impact validated | Projected business metric improvement documented | |
| [ ] Edge case review | Business edge cases tested (holidays, market events, etc.) | |
| [ ] Fallback behavior defined | What happens when model is unavailable | |
| [ ] A/B test plan (if applicable) | Experiment design reviewed and approved | |

**Gate owner:** Business stakeholder  
**Override authority:** Business unit head

---

## 2. Deployment Approval Process

### 2.1 Approval Chain

| Step | Approver | What they verify | Timeline |
|------|----------|-----------------|----------|
| 1. Technical review | ML team peer | Code quality, methodology, reproducibility | 1–2 days |
| 2. Evaluation sign-off | ML team lead | Metrics meet requirements, edge cases covered | 1 day |
| 3. Fairness sign-off | Compliance/Model Risk | Bias checks pass, documentation adequate | 1–2 days |
| 4. Business sign-off | Business owner | Business logic validated, impact understood | 1 day |
| 5. Deployment approval | MLOps/Platform lead | Infra ready, rollback plan solid, monitoring in place | 1 day |

**Total minimum approval time:** 3–5 business days (for standard deployments)

### 2.2 Expedited Approval (Emergency Retraining)

For urgent retraining (active accuracy degradation, drift emergency):

| Step | Approver | Timeline |
|------|----------|----------|
| 1. Evaluation gate (automated) | Pipeline | Minutes |
| 2. ML team lead sign-off | Verbal/Slack + documented post-hoc | < 1 hour |
| 3. MLOps deployment approval | Verbal/Slack + documented post-hoc | < 30 minutes |
| 4. Compliance notification | FYI notification, full review within 48h | Post-deployment |

**Conditions for expedited approval:**
- Active P1/P2 incident in progress
- Retraining uses same pipeline (no methodology changes)
- Evaluation metrics meet or exceed current model
- Full approval documentation completed within 48 hours post-deployment

### 2.3 Approval Documentation

Each approval must be recorded with:
- [ ] Approver name and role
- [ ] Date and time of approval
- [ ] Evidence reviewed (metrics report, bias report, etc.)
- [ ] Any conditions or caveats on the approval
- [ ] Approval stored in immutable audit log

---

## 3. Post-Deployment Monitoring Requirements

### 3.1 First 24 Hours (Deployment Watch)

| Check | Frequency | Action if violated |
|-------|-----------|-------------------|
| Serving health (HTTP errors, latency) | Continuous | Immediate rollback |
| Prediction distribution vs expected | Hourly | Investigate, consider rollback |
| Feature distribution vs training | Hourly | Investigate |
| Error rate vs previous model | Hourly | Rollback if > 2x previous |
| Business metric impact (if A/B) | Hourly | Stop experiment if harmful |

**On-call requirement:** Deployer stays available for 24 hours post-deployment.

### 3.2 First Week

| Check | Frequency | Action if violated |
|-------|-----------|-------------------|
| All first-24-hour checks | Continue at reduced frequency (4x daily) | Per above |
| Accuracy/precision/recall vs SLO | Daily | Investigate, prepare rollback |
| Drift monitoring | Daily | Document, assess risk |
| Segment-level performance | Daily | Investigate any segment degradation |
| Fairness metrics | Daily | Escalate to compliance if threshold approached |

### 3.3 Ongoing (Steady State)

| Check | Frequency | Action if violated |
|-------|-----------|-------------------|
| Serving health | Continuous (automated) | Page on-call |
| Accuracy vs SLO | Daily (automated) | Alert → triage → respond |
| Drift scores | Daily (automated) | Alert if above threshold |
| Data quality checks | On every pipeline run | Alert + block if severe |
| Fairness metrics | Weekly (automated) | Alert → compliance review |
| Model staleness | Weekly | Flag if model age > threshold |
| Resource utilization | Weekly | Capacity planning |

---

## 4. Regular Review Cadence

### 4.1 Weekly Model Health Check (15 minutes)

**Attendees:** MLOps on-call, ML team lead  
**Agenda:**
- [ ] Review active alerts and drift status for all models
- [ ] Check model age vs retraining schedule compliance
- [ ] Review any data quality incidents from past week
- [ ] Flag models approaching thresholds

### 4.2 Monthly Model Health Review (1 hour)

**Attendees:** MLOps lead, ML team lead, Data Science lead, Business stakeholder  
**Agenda:**
- [ ] Review all production model performance trends
- [ ] Assess drift patterns — any models needing proactive retraining?
- [ ] Review fairness metrics trends across all models
- [ ] Review incident count and patterns from past month
- [ ] Discuss upcoming data changes that could impact models
- [ ] Review model age compliance (are any past due for retraining?)
- [ ] Capacity planning for upcoming model deployments
- [ ] Action items from previous month — status check

**Output:** Monthly model health report (store in governance repository)

### 4.3 Quarterly Governance Review (2 hours)

**Attendees:** All monthly attendees + Compliance + Risk + Executive sponsor  
**Agenda:**
- [ ] Review all models for continued business relevance
- [ ] Compliance status check — documentation complete for all models?
- [ ] Fairness audit results for the quarter
- [ ] Review of incidents — systemic patterns?
- [ ] Assess need to retire any models
- [ ] Review governance process itself — working well? Needs updates?
- [ ] Regulatory landscape updates — any new requirements?
- [ ] Budget and resourcing for upcoming quarter

**Output:** Quarterly governance report for executive team + regulatory file

### 4.4 Annual Model Validation (per model)

**Triggered:** 12 months after last validation, or upon significant change  
**Attendees:** Independent validation team (not the team that built the model)  
**Scope:**
- [ ] Independent evaluation on fresh holdout data
- [ ] Methodology review — still appropriate for the problem?
- [ ] Data source review — still representative and reliable?
- [ ] Bias/fairness deep dive with current data
- [ ] Documentation completeness audit
- [ ] Comparison against alternative approaches
- [ ] Recommendation: continue / retrain / retire / rebuild

---

## 5. Compliance Documentation

### 5.1 Model Card Template

Every production model must have a model card with these sections:

```
MODEL CARD: [Model Name]

1. Model Overview
   - Name and version
   - Purpose and intended use
   - Out-of-scope uses (what it should NOT be used for)
   - Model owner and team

2. Model Architecture
   - Algorithm type
   - Key hyperparameters
   - Input features (list with descriptions)
   - Output format and interpretation

3. Training Data
   - Source(s) and date range
   - Size (rows, features)
   - Known limitations or biases in data
   - Data preprocessing steps

4. Evaluation
   - Metrics and values
   - Performance across segments/demographics
   - Known failure modes
   - Comparison to baseline/previous version

5. Fairness Analysis
   - Protected classes assessed
   - Fairness metrics and results
   - Known limitations
   - Mitigation steps taken

6. Operational Requirements
   - Latency requirements
   - Throughput requirements
   - Resource requirements
   - Dependencies (data pipelines, feature stores)

7. Monitoring and Maintenance
   - SLOs defined
   - Alerts configured
   - Retraining schedule/triggers
   - Review cadence

8. Risks and Limitations
   - Known failure conditions
   - Edge cases with poor performance
   - Scenarios where model should not be trusted
   - Fallback behavior when model is unavailable

9. Changelog
   - Version history with dates and changes
```

### 5.2 Data Sheet Requirements

Every training dataset must have a data sheet:

```
DATA SHEET: [Dataset Name]

1. Motivation
   - Why was this dataset created?
   - Who created it?
   - Who funded it?

2. Composition
   - What does each instance represent?
   - How many instances?
   - What data types are included?
   - Is there missing data? How handled?
   - Does it contain PII?

3. Collection Process
   - How was data collected?
   - What time period does it cover?
   - Were there any filtering steps?
   - Who collected the data?

4. Preprocessing
   - What preprocessing was done?
   - What raw data was discarded?
   - Were there any transformations?

5. Uses
   - What tasks has this dataset been used for?
   - What tasks should it NOT be used for?
   - Is there anything about the dataset that might
     impact future uses?

6. Distribution and Maintenance
   - How is the dataset stored and accessed?
   - Who maintains it?
   - How often is it updated?
   - How are errors corrected?

7. Legal and Ethical
   - Were there any ethical review processes?
   - Does the data relate to people?
   - Were there consent procedures?
   - Are there regulatory considerations?
```

---

## 6. Audit Trail Requirements

### 6.1 What Must Be Logged (Immutably)

| Event | Required metadata |
|-------|-------------------|
| **Training initiated** | Who triggered, data version, code commit, config version, timestamp |
| **Training completed** | Duration, final metrics, artifacts produced, resource usage |
| **Evaluation run** | Metrics calculated, pass/fail on each gate, evaluator |
| **Model registered** | Version assigned, registry location, metadata attached |
| **Approval granted** | Approver identity, evidence reviewed, conditions, timestamp |
| **Deployment initiated** | Target environment, deployment method, deployer, timestamp |
| **Deployment completed** | Health check results, canary results, final status |
| **Prediction served** | (Sampled) Input hash, output, model version, timestamp, latency |
| **Drift detected** | Feature(s), score(s), threshold, action taken |
| **Incident created** | Severity, type, initial assessment, responder |
| **Rollback executed** | Reason, who decided, from version, to version, timestamp |
| **Model retired** | Reason, replacement (if any), who decided, timestamp |
| **Configuration changed** | What changed, who changed it, old value, new value |
| **Access granted/revoked** | Who, what access, by whom, reason |

### 6.2 Audit Log Requirements

| Requirement | Specification |
|-------------|--------------|
| **Immutability** | Logs cannot be modified or deleted after creation |
| **Retention** | Minimum 7 years (banking regulatory requirement) |
| **Accessibility** | Searchable by model, date range, event type, person |
| **Integrity** | Tamper-evident (checksums or blockchain-style linking) |
| **Completeness** | No gaps in the timeline for any model |
| **Timeliness** | Events logged within 1 minute of occurrence |

### 6.3 Audit Preparation Checklist

When audit is announced:

| Step | Action | Status |
|------|--------|--------|
| [ ] Identify models in scope | List all models covered by the audit | |
| [ ] Verify documentation completeness | Model cards, data sheets, monitoring plans | |
| [ ] Verify audit trail completeness | No gaps in logging for in-scope period | |
| [ ] Prepare model lineage reports | Full lineage from data to deployed model | |
| [ ] Prepare fairness reports | Current + historical fairness metrics | |
| [ ] Prepare incident history | All incidents, postmortems, action items | |
| [ ] Verify reproducibility | Can you recreate any historical model version? | |
| [ ] Identify and document exceptions | Any governance exceptions and their justification | |
| [ ] Prepare change history | All changes to models, data, pipelines | |
| [ ] Brief the team | Everyone knows what auditors may ask | |

---

## 7. Governance Exceptions

Sometimes gates must be bypassed. Every exception must be:

| Requirement | Details |
|-------------|---------|
| **Documented** | What gate was bypassed and why |
| **Approved** | By someone senior enough to accept the risk (one level above normal approver) |
| **Time-bounded** | Exception has an expiration date |
| **Tracked** | Included in quarterly governance review |
| **Remediated** | Plan to close the exception within the time bound |

### Exception Log

| Date | Model | Gate bypassed | Justification | Approved by | Expires | Remediation plan | Status |
|------|-------|--------------|---------------|-------------|---------|-----------------|--------|
| | | | | | | | |

---

## Quick Reference: Deployment Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MODEL DEPLOYMENT WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. TRAIN → Pipeline produces candidate model                        │
│       │                                                              │
│  2. EVALUATE → Automated metrics gates (pass/fail)                   │
│       │                                                              │
│  3. DOCUMENT → Model card, data sheet, monitoring plan               │
│       │                                                              │
│  4. REVIEW → Bias check, security check, business validation         │
│       │                                                              │
│  5. APPROVE → Approval chain (1-5 days)                              │
│       │                                                              │
│  6. DEPLOY → Canary deployment with monitoring                       │
│       │                                                              │
│  7. WATCH → 24-hour deployment watch, then steady-state monitoring   │
│       │                                                              │
│  8. MAINTAIN → Regular reviews, retraining, eventual retirement      │
│                                                                      │
│  At any point: ROLLBACK if issues detected (per SLA)                 │
│  At any point: DOCUMENT everything in audit trail                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```
