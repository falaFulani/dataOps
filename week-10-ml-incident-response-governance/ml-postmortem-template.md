# ML Incident Postmortem Template

**Purpose:** Blameless postmortem template extended with ML-specific sections. Use after every P1/P2 incident and optionally for P3 incidents with learning value.

**Principle:** We focus on systems, processes, and tooling — not people. "How did our system allow this to happen?" not "Who made this happen?"

---

## Postmortem: [Incident Title]

**Date of incident:** YYYY-MM-DD  
**Date of postmortem:** YYYY-MM-DD  
**Postmortem lead:** [Name]  
**Attendees:** [Names and roles]

---

## 1. Executive Summary

_Two to three sentences. What happened, what was the impact, how was it resolved._

> Example: "Our fraud detection model's precision dropped from 0.92 to 0.78 over a two-week period due to concept drift caused by a new fraud pattern our model hadn't seen. Approximately 1,200 legitimate transactions were incorrectly flagged. We retrained on recent labeled data and deployed within 6 hours of detection."

---

## 2. Impact

### Business Impact
| Metric | Value |
|--------|-------|
| Duration of impact | [e.g., 14 days undetected + 6 hours to resolve] |
| Predictions affected | [e.g., ~50,000 predictions during impacted period] |
| Incorrect predictions | [e.g., ~1,200 false positives above normal rate] |
| Revenue/cost impact | [quantify if possible] |
| Customer impact | [e.g., 1,200 customers had transactions incorrectly held] |
| SLO violation | [which SLO, how much error budget burned] |

### Severity Classification
- **Severity:** P1 / P2 / P3 / P4
- **Incident type:** Drift / Data quality / Pipeline failure / Serving error / Bias / Training failure

### Regulatory Impact
- **Regulatory notification required?** Yes / No
- **Protected classes affected?** Yes / No
- **Audit trail preserved?** Yes / No

---

## 3. Timeline

_Detailed timeline with timestamps. Include when the issue likely started, when it was detectable, and when it was actually detected._

| Time (UTC) | Event |
|------------|-------|
| YYYY-MM-DD HH:MM | **Issue likely started** — [what changed in the world/data] |
| YYYY-MM-DD HH:MM | **Issue first detectable** — [when monitoring could have caught it] |
| YYYY-MM-DD HH:MM | **Alert fired** — [which alert, what threshold] |
| YYYY-MM-DD HH:MM | **Triage started** — [who responded, what they checked first] |
| YYYY-MM-DD HH:MM | **Root cause identified** — [what was found] |
| YYYY-MM-DD HH:MM | **Mitigation started** — [rollback/retrain/fix initiated] |
| YYYY-MM-DD HH:MM | **Resolution deployed** — [new model/fix deployed] |
| YYYY-MM-DD HH:MM | **Verified resolved** — [metrics confirmed recovered] |

### Detection Lag Analysis

| Milestone | Timestamp | Gap |
|-----------|-----------|-----|
| Issue started | [time] | — |
| Issue was detectable | [time] | Time to detectability: ___ |
| Alert actually fired | [time] | **Detection lag: ___** |
| Human acknowledged | [time] | Acknowledgement time: ___ |
| Resolution deployed | [time] | Time to resolve: ___ |

**Total time to detect:** [how long the issue existed before we knew]  
**Total time to resolve:** [from detection to resolution]  
**Why the detection lag?** [What monitoring gap allowed this to go undetected?]

---

## 4. Root Cause Analysis

### Root Cause Category
- [ ] Data drift (input distribution shifted)
- [ ] Concept drift (relationship between inputs and outputs changed)
- [ ] Data quality degradation (upstream data corrupted/stale/missing)
- [ ] Pipeline failure (training/serving pipeline broke)
- [ ] Code/config change (deployment introduced a bug)
- [ ] Infrastructure failure (serving platform issue)
- [ ] Model staleness (model too old for current patterns)
- [ ] Bias introduced/amplified
- [ ] External event (market shift, regulation change, etc.)
- [ ] Other: ___

### Root Cause Description

_Detailed description of what caused the incident. Go at least 3 levels deep in "why."_

**What happened:**  
> [Description of the failure]

**Why did it happen:**  
> [Immediate cause]

**Why did that happen:**  
> [Underlying cause]

**Why did that happen:**  
> [Systemic/organizational cause]

### Contributing Factors

_What didn't cause the incident but made it worse or harder to detect/resolve?_

1. [Contributing factor 1]
2. [Contributing factor 2]
3. [Contributing factor 3]

---

## 5. ML-Specific Analysis

### 5.1 Model Version Information

| Field | Value |
|-------|-------|
| Model name | [e.g., fraud-detection-v2] |
| Model version (at incident time) | [e.g., v2.3.1] |
| Model framework | [e.g., XGBoost 1.7.4] |
| Training date | [when was the serving model trained] |
| Training data date range | [what data was it trained on] |
| Model age at incident | [how old was the model] |
| Previous retraining date | [when was it last retrained] |
| Model version (after resolution) | [what version replaced it] |

### 5.2 Drift Analysis

_If drift was involved, provide the statistical evidence._

| Feature/Metric | Training distribution | Incident distribution | Drift score (PSI/KL) |
|---------------|----------------------|----------------------|---------------------|
| [feature 1] | [summary stats] | [summary stats] | [score] |
| [feature 2] | [summary stats] | [summary stats] | [score] |
| Overall prediction distribution | [summary] | [summary] | [score] |

**Drift type:** Data drift / Concept drift / Prediction drift / Training-serving skew  
**Drift severity:** Minor / Moderate / Severe  
**Drift started approximately:** [date/time]  
**Drift cause (if known):** [e.g., new fraud pattern, seasonal shift, upstream schema change]

### 5.3 Data Lineage

_What data was involved in both the problem and the resolution?_

| Data aspect | Details |
|-------------|---------|
| Training data source | [source system(s)] |
| Training data version | [version/timestamp] |
| Feature pipeline version | [version/commit] |
| Serving data source | [where live features come from] |
| Data quality at incident time | [were data validation checks passing?] |
| Data issue (if applicable) | [what was wrong with the data] |

### 5.4 Retraining Decision Rationale

_Document why you chose the response you did._

**Decision made:** Retrain / Rollback / Fix data / Monitor only / Suspend model

**Why this decision:**
> [Explain the rationale. Reference the retraining decision tree.]

**Alternatives considered:**
| Option | Pros | Cons | Why rejected |
|--------|------|------|-------------|
| [Option A] | | | |
| [Option B] | | | |

**Decision maker:** [Name/role]  
**Compliance consulted:** Yes / No / N/A

---

## 6. Resolution

### What fixed it
_Detailed description of the resolution._

> [What was done to resolve the incident]

### Verification
_How did we confirm the fix worked?_

- [ ] Metrics recovered to within SLO
- [ ] No recurrence within 24 hours
- [ ] Stakeholders confirmed business impact resolved
- [ ] Compliance signed off (if applicable)

---

## 7. Action Items

### Monitoring Improvements
_How do we detect this faster next time?_

| Action | Owner | Due date | Status |
|--------|-------|----------|--------|
| [e.g., Add alert for precision drop > 5% over 48h] | [Name] | [Date] | [ ] Open |
| [e.g., Reduce drift monitoring window from weekly to daily] | [Name] | [Date] | [ ] Open |
| [e.g., Add data freshness check for upstream source X] | [Name] | [Date] | [ ] Open |

### Pipeline Hardening
_How do we prevent this category of failure?_

| Action | Owner | Due date | Status |
|--------|-------|----------|--------|
| [e.g., Add automated drift-triggered retraining] | [Name] | [Date] | [ ] Open |
| [e.g., Add schema validation to feature pipeline input] | [Name] | [Date] | [ ] Open |
| [e.g., Implement shadow model comparison in production] | [Name] | [Date] | [ ] Open |

### Process Improvements
_How do we improve our response process?_

| Action | Owner | Due date | Status |
|--------|-------|----------|--------|
| [e.g., Update runbook with this scenario] | [Name] | [Date] | [ ] Open |
| [e.g., Add this failure mode to on-call training] | [Name] | [Date] | [ ] Open |
| [e.g., Establish regular model health review cadence] | [Name] | [Date] | [ ] Open |

### Training/Model Improvements
_How do we improve the model's robustness?_

| Action | Owner | Due date | Status |
|--------|-------|----------|--------|
| [e.g., Retrain with wider date range to capture seasonality] | [Name] | [Date] | [ ] Open |
| [e.g., Add monitoring for this specific drift pattern] | [Name] | [Date] | [ ] Open |
| [e.g., Evaluate ensemble approach for robustness] | [Name] | [Date] | [ ] Open |

---

## 8. Follow-up Metrics

_Track these over the next 30/60/90 days to confirm the fix is durable._

| Metric | Baseline (pre-incident) | At incident | Current | 30-day target |
|--------|------------------------|-------------|---------|---------------|
| [Primary metric, e.g., Precision] | [value] | [value] | [value] | [target] |
| [Secondary metric] | [value] | [value] | [value] | [target] |
| [Detection time for this failure mode] | [was infinite] | — | [current] | [target] |
| [Data quality score] | [value] | [value] | [value] | [target] |

### Review Schedule

| Review | Date | Purpose |
|--------|------|---------|
| 1-week check | [date] | Confirm metrics stable, no recurrence |
| 30-day review | [date] | Check action items progress, verify fix durability |
| 90-day review | [date] | Close postmortem, confirm systemic improvements |

---

## 9. Lessons Learned

### What went well
1. [e.g., Escalation was smooth, right people engaged quickly]
2. [e.g., Runbook was helpful for initial triage]
3. [e.g., Monitoring caught the issue before customer complaints]

### What didn't go well
1. [e.g., Detection took 14 days — unacceptable for this model]
2. [e.g., No clear owner for drift incidents in escalation matrix]
3. [e.g., Retraining took 6 hours because pipeline wasn't ready]

### Where we got lucky
1. [e.g., Impact was on low-risk predictions, not high-risk ones]
2. [e.g., A team member happened to notice the dashboard during routine check]

---

## 10. Sign-off

| Role | Name | Sign-off date |
|------|------|---------------|
| Postmortem lead | | |
| ML team lead | | |
| Platform/MLOps lead | | |
| Compliance (if applicable) | | |
| Business stakeholder (if P1/P2) | | |

---

## Appendix

### A. Supporting Data
_Attach or link: drift reports, monitoring screenshots, pipeline logs, etc._

### B. Related Incidents
_Link to similar past incidents, if any._

### C. References
_Link to: model card, monitoring dashboard, pipeline definition, governance checklist._
