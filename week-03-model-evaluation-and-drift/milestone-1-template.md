# Milestone 1: ML Failure Modes Runbook

> **Author:** Alex Mashua  
> **Date:** ___________  
> **Context:** This runbook is for the ML Support Team's first responders.
> When an ML model alert fires, this is the document you grab.

---

## How to Use This Runbook

1. Alert fires → Identify which failure mode matches
2. Follow immediate response steps
3. Classify severity and escalate if needed
4. Investigate root cause using the checklist
5. Execute resolution
6. Document and add to post-incident review

---

## Failure Mode 1: Data Drift (No Accuracy Drop Yet)

### Detection
- **Alert trigger:** _________________________________
- **Monitoring tool:** _________________________________
- **Threshold:** _________________________________

### Severity Classification
- **Level:** P___  
- **Justification:** _________________________________

### Immediate Response (first 15 minutes)
1. _________________________________
2. _________________________________
3. _________________________________

### Root Cause Investigation
- [ ] Check upstream data sources for changes
- [ ] Identify which features drifted and by how much
- [ ] Determine if drift is gradual or sudden
- [ ] Check for recent changes in data ingestion pipelines
- [ ] _________________________________

### Resolution Options
| Option | When to Use | Risks |
|--------|-------------|-------|
| Monitor & wait | _____________ | _____________ |
| Retrain on new data | _____________ | _____________ |
| Adjust alert thresholds | _____________ | _____________ |

### Prevention / Monitoring
- _________________________________
- _________________________________

---

## Failure Mode 2: Data Drift WITH Accuracy Drop

### Detection
- **Alert trigger:** _________________________________
- **Monitoring tool:** _________________________________
- **Threshold:** _________________________________

### Severity Classification
- **Level:** P___  
- **Justification:** _________________________________

### Immediate Response (first 15 minutes)
1. _________________________________
2. _________________________________
3. _________________________________

### Root Cause Investigation
- [ ] Confirm accuracy drop with ground truth data
- [ ] Correlate timing of drift with accuracy degradation
- [ ] Determine if a fallback/rule-based system should take over
- [ ] _________________________________
- [ ] _________________________________

### Resolution Options
| Option | When to Use | Risks |
|--------|-------------|-------|
| Rollback to previous model | _____________ | _____________ |
| Retrain on new data | _____________ | _____________ |
| Switch to fallback rules | _____________ | _____________ |
| _______________ | _____________ | _____________ |

### Prevention / Monitoring
- _________________________________
- _________________________________

---

## Failure Mode 3: Concept Drift Suspected

### Detection
- **Alert trigger:** _________________________________
- **Monitoring tool:** _________________________________
- **Threshold:** _________________________________
- **Note:** How do you detect this when data drift checks are clean?

### Severity Classification
- **Level:** P___  
- **Justification:** _________________________________

### Immediate Response (first 15 minutes)
1. _________________________________
2. _________________________________
3. _________________________________

### Root Cause Investigation
- [ ] Compare model predictions vs actual outcomes (ground truth)
- [ ] Check for business/market changes that alter what's "normal"
- [ ] Interview stakeholders: has anything changed in the real world?
- [ ] _________________________________
- [ ] _________________________________

### Resolution Options
| Option | When to Use | Risks |
|--------|-------------|-------|
| Retrain with new labels | _____________ | _____________ |
| Redesign features | _____________ | _____________ |
| Switch to rule-based fallback | _____________ | _____________ |
| _______________ | _____________ | _____________ |

### Prevention / Monitoring
- _________________________________
- _________________________________

---

## Failure Mode 4: Training-Serving Skew (Post-Deploy)

### Detection
- **Alert trigger:** _________________________________
- **Monitoring tool:** _________________________________
- **Threshold:** _________________________________

### Severity Classification
- **Level:** P___  
- **Justification:** _________________________________

### Immediate Response (first 15 minutes)
1. _________________________________
2. _________________________________
3. _________________________________

### Root Cause Investigation
- [ ] Identify what was deployed and when
- [ ] Compare feature values at serving time vs training time
- [ ] Diff the feature transformation code between versions
- [ ] Check for library version mismatches
- [ ] _________________________________

### Resolution Options
| Option | When to Use | Risks |
|--------|-------------|-------|
| Rollback the deploy | _____________ | _____________ |
| Hotfix the pipeline code | _____________ | _____________ |
| _______________ | _____________ | _____________ |

### Prevention / Monitoring
- _________________________________
- _________________________________

---

## Failure Mode 5: Sudden Prediction Drift (Unknown Cause)

### Detection
- **Alert trigger:** _________________________________
- **Monitoring tool:** _________________________________
- **Threshold:** _________________________________

### Severity Classification
- **Level:** P___  
- **Justification:** _________________________________

### Immediate Response (first 15 minutes)
1. _________________________________
2. _________________________________
3. _________________________________

### Root Cause Investigation
- [ ] Check for data drift (is input distribution different?)
- [ ] Check for recent deploys (training-serving skew?)
- [ ] Check upstream data sources (schema changes? missing data?)
- [ ] Check if ground truth indicates concept drift
- [ ] _________________________________

### Resolution Options
| Option | When to Use | Risks |
|--------|-------------|-------|
| Increase monitoring granularity | _____________ | _____________ |
| Activate fallback model | _____________ | _____________ |
| Escalate to data science | _____________ | _____________ |
| _______________ | _____________ | _____________ |

### Prevention / Monitoring
- _________________________________
- _________________________________

---

## Escalation Matrix

| Severity | Response SLA | Resolution SLA | Who Gets Paged |
|----------|-------------|----------------|----------------|
| P1 (Critical) | _____ min | _____ hours | ______________ |
| P2 (High) | _____ min | _____ hours | ______________ |
| P3 (Warning) | _____ min | _____ hours | ______________ |
| P4 (Info) | _____ | _____ | ______________ |

---

## Post-Incident Template

After any P1/P2 ML incident, document:

1. **Timeline:** When did drift start? When was it detected? When was it resolved?
2. **Detection gap:** How long between drift start and alert? Can we close this gap?
3. **Impact:** What was the business impact during the degradation period?
4. **Root cause:** Which drift type? What caused it?
5. **Resolution:** What fixed it? How long did resolution take?
6. **Prevention:** What monitoring/testing/process changes prevent recurrence?

---

*Complete this template after finishing the Week 3 lab. 
Use specific metrics, thresholds, and tool names where possible.*
