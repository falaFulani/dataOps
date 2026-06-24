# Week 3: Model Evaluation & The Drift Family

> **Ops Translation:** If Week 1 was "what is this system?" and Week 2 was "how do we build it?", Week 3 is "how do we know it's broken?" — this is your monitoring, alerting, and incident classification week.

---

## Learning Objectives

By the end of this week, you will:
- Understand the core model evaluation metrics and when each matters
- Read a confusion matrix like you read a Grafana dashboard
- **Know the drift family cold** — these are your ML incident categories
- Map each drift type to detection → alert → response (your runbook thinking)
- Run Evidently AI to generate drift reports (lab)

---

## 1. Model Evaluation Metrics

### The Big Four

Think of these as SLIs (Service Level Indicators) for your model. Each one tells you something different about model health.

| Metric | What It Measures | Ops Analogy |
|--------|-----------------|-------------|
| **Accuracy** | % of all predictions that were correct | Overall uptime % |
| **Precision** | Of items flagged positive, % that were actually positive | Alert signal-to-noise ratio |
| **Recall** | Of actual positives, % the model caught | Detection coverage |
| **F1 Score** | Harmonic mean of Precision & Recall | Balanced health score |

### When Each Metric Matters

#### Accuracy
- **Formula:** (Correct predictions) / (Total predictions)
- **When it matters:** Balanced datasets where each class is roughly equal
- **When it LIES:** Imbalanced data. If 99% of transactions are legit, a model that says "everything is legit" gets 99% accuracy but catches zero fraud.
- **Bank example:** Classifying customer segments (roughly equal distribution)

#### Precision
- **Formula:** True Positives / (True Positives + False Positives)
- **Translation:** "When the model raises an alert, how often is it a real issue?"
- **When it matters:** When false alarms are expensive
- **Bank example:** Blocking a legitimate customer's card (false positive) = angry customer, lost revenue, complaint calls. You want HIGH precision here.

#### Recall
- **Formula:** True Positives / (True Positives + False Negatives)
- **Translation:** "Of all the real issues out there, how many did we catch?"
- **When it matters:** When missing a real positive is catastrophic
- **Bank example:** Missing actual fraud (false negative) = financial loss, regulatory risk. You want HIGH recall in fraud detection.

#### F1 Score
- **Formula:** 2 × (Precision × Recall) / (Precision + Recall)
- **Translation:** A single number that balances precision and recall
- **When it matters:** When you need to compare models and can't afford to tank either precision or recall
- **Bank example:** Anti-money laundering detection — you need to catch patterns (recall) but compliance teams can't drown in false alerts (precision)

### The Precision-Recall Tradeoff

This is like the availability-vs-security tradeoff you already know:
- Crank up recall → you catch more fraud, but also flag more legit transactions (more noise)
- Crank up precision → fewer false alarms, but you miss more real fraud (less coverage)

**Your job as an ops leader:** Understand what tradeoff your ML engineers chose and whether it still makes sense for the business.

---

## 2. The Confusion Matrix

A confusion matrix is a 2×2 table (for binary classification) that shows exactly where the model gets it right and wrong.

```
                    PREDICTED
                 Positive  | Negative
              ┌────────────┼────────────┐
ACTUAL  Pos   │     TP     │     FN     │
              ├────────────┼────────────┤
ACTUAL  Neg   │     FP     │     TN     │
              └────────────┼────────────┘
```

| Cell | Meaning | Ops Analogy |
|------|---------|-------------|
| **TP** (True Positive) | Model said fraud, it WAS fraud | Real alert, real incident |
| **TN** (True Negative) | Model said legit, it WAS legit | No alert, no incident (quiet shift) |
| **FP** (False Positive) | Model said fraud, it was LEGIT | False alarm / noisy alert |
| **FN** (False Negative) | Model said legit, it WAS fraud | Missed incident — silent failure |

**Ops wisdom that transfers directly:** FPs burn out your team (alert fatigue). FNs burn down your business (undetected failures). The confusion matrix tells you which failure mode dominates.

---

## 3. The Drift Family — LEARN THESE COLD

> ⚠️ **This is the most important section for your interview prep.** Drift types are the ML equivalent of incident categories. When someone says "the model is degrading," your first question should be: "which type of drift?"

### Overview

| Drift Type | One-Liner | Ops Equivalent |
|-----------|-----------|---------------|
| **Data Drift** | Live inputs look different from training data | Config drift / environment drift |
| **Concept Drift** | The real-world rules changed | Business logic change nobody told the system about |
| **Prediction Drift** | Model's output distribution shifted | SLI trend change — leading indicator |
| **Training-Serving Skew** | Prod data pipeline ≠ training data pipeline | Dev/prod environment mismatch |

---

### 3.1 Data Drift

**What it is:** The statistical distribution of incoming (live) data has shifted from what the model saw during training.

**Real example:** Your fraud model was trained on transaction data from 2019–2022. In 2023, your bank launches a new crypto trading feature. Suddenly the model sees transaction amounts, frequencies, and merchant categories it never encountered in training.

**How to detect:**
- Statistical tests comparing feature distributions (KS test, PSI — Population Stability Index)
- Monitoring input feature statistics over time (mean, variance, percentiles)
- Evidently AI drift reports (we'll do this in the lab)

**Ops analogy:** This is like config drift. Your servers were provisioned with certain specs, but over time someone manually changed things. The system "expects" one environment but is operating in another.

**Key insight:** Data drift doesn't always mean the model is wrong NOW — but it means the model is operating outside its tested conditions. It's a leading indicator.

---

### 3.2 Concept Drift

**What it is:** The underlying relationship between inputs and the correct output has changed. The ground truth shifted.

**Real example:** Your fraud model learned that "multiple small transactions under $50 across 5+ merchants in an hour = fraud." Then a new legitimate fintech app launches that does exactly this pattern for cashback optimization. What WAS fraud is now a normal customer behavior. The concept of "fraud" itself drifted.

**How to detect:**
- Model accuracy drops when measured against ground truth labels
- Business feedback: "the model is flagging too many legit customers" (or missing fraud)
- Comparing model predictions vs. actual outcomes over time windows
- Delayed — you often can't detect this until labeled data arrives

**Ops analogy:** This is when the business logic changes but nobody updated the system. Like when your company acquires another business, customers now log in from a new country, but your geo-blocking rules still flag them.

**Key insight:** Concept drift is the hardest to detect quickly because you need ground truth labels, and those often arrive with a delay (was that transaction actually fraud? You might not know for 30 days).

---

### 3.3 Prediction Drift

**What it is:** The distribution of the model's outputs (predictions) is shifting, even if you don't have ground truth yet.

**Real example:** Your fraud model normally flags 2% of transactions. This week it's flagging 8%. You don't know yet if those are real fraud or false positives — but something changed.

**How to detect:**
- Monitor prediction distribution over time (% flagged, score distribution)
- Statistical tests on output distributions (comparing windows)
- Simple threshold: "if % predicted positive changes by more than X%, alert"

**Ops analogy:** This is like watching your error rate trend. You don't know root cause yet, but you see the symptom. It's your first-responder metric.

**Key insight:** Prediction drift is often the FIRST thing you'll notice because you don't need ground truth. It's your canary. Then you investigate whether it's data drift, concept drift, or something else causing it.

---

### 3.4 Training-Serving Skew

**What it is:** The data processing pipeline in production differs from the one used during training. The model was trained on data processed one way, but live data is processed differently.

**Real example:** During training, your feature engineering normalizes transaction amounts using the global mean ($47.50). In production, a different team implemented the pipeline and used a running average that starts at $0 on each service restart. The model sees completely different feature values despite the raw inputs being normal.

**How to detect:**
- Compare feature distributions at inference time vs. training time
- Integration tests that run the same raw input through both pipelines
- Monitor for sudden shifts after deployments (especially of data pipelines)
- Unit tests on feature transformation logic

**Ops analogy:** This is your classic "works in dev, breaks in prod." Different library versions, different configs, different data paths. A deployment mismatch.

**Key insight:** This one is the most preventable and the most embarrassing. It's a software engineering failure, not a data science problem. YOUR domain.

---

## 4. Detection Strategies

### What To Monitor

| Layer | What To Watch | Tools |
|-------|--------------|-------|
| **Input data** | Feature distributions, missing values, schema | Evidently, Great Expectations |
| **Model outputs** | Prediction distribution, confidence scores | Evidently, custom Prometheus metrics |
| **Business outcomes** | Accuracy vs. ground truth (delayed) | Custom dashboards, labeling pipelines |
| **Pipeline health** | Feature computation correctness, latency | Standard APM + data pipeline tests |

### Detection Timeline

```
Minutes  → Prediction drift (output distribution shifted)
Hours    → Data drift (input distribution shifted)  
Days     → Training-serving skew (usually caught after a deploy)
Weeks    → Concept drift (need ground truth labels to confirm)
```

---

## 5. Response Framework: Retrain vs Rollback vs Investigate

| Scenario | Action | Reasoning |
|----------|--------|-----------|
| Prediction drift after YOUR deploy | **Rollback** | Training-serving skew likely — your pipeline change broke something |
| Gradual data drift, no accuracy drop yet | **Investigate** | Monitor closely, prepare retraining data, don't panic |
| Sudden data drift + accuracy drop | **Retrain** on new data | The world changed, model needs to learn new patterns |
| Concept drift confirmed | **Retrain** (maybe redesign) | Ground truth shifted, old model learns wrong things |
| Training-serving skew identified | **Fix the pipeline** | This is a bug, not a modeling problem |
| Prediction drift, no root cause found | **Investigate** then escalate | Don't retrain blindly — find the cause first |

### Decision Tree

```
Model degradation detected
├── Did we deploy anything recently?
│   ├── YES → Check for training-serving skew → Fix pipeline or Rollback
│   └── NO → Continue...
├── Is input data distribution different?
│   ├── YES → Data drift → Is model accuracy impacted?
│   │   ├── YES → Retrain on new data distribution
│   │   └── NO → Monitor, prepare retrain pipeline
│   └── NO → Continue...
├── Do we have ground truth showing accuracy drop?
│   ├── YES → Concept drift → Retrain (possibly new features/architecture)
│   └── NO → Continue monitoring, collect labels
└── Unknown → Escalate to data science team with evidence
```

---

## 6. The Mapping Table: Drift → Alert → Runbook

> This is your interview gold. Memorize the pattern: detect → classify → respond.

| Drift Type | Alert Trigger | Severity | Immediate Action | Resolution |
|-----------|--------------|----------|-----------------|------------|
| **Data Drift** | PSI > 0.2 on key features OR feature distribution KS test p < 0.01 | P3 (Warning) | Notify data engineering, check upstream data sources | Investigate source; retrain if accuracy drops |
| **Concept Drift** | Model accuracy drops >5% vs. baseline on labeled holdout set | P2 (High) | Alert data science lead, begin impact assessment | Retrain with new labeled data; may need feature redesign |
| **Prediction Drift** | Output distribution shifts >2 std deviations from baseline | P3→P2 (Escalating) | Check for data drift first; if none found, investigate model internals | Depends on root cause (may be symptom of data or concept drift) |
| **Training-Serving Skew** | Feature values at inference differ >10% from training stats post-deploy | P2 (High) | Rollback last pipeline/infra deploy | Fix data pipeline code; add integration tests |

### Hypothetical Alert Examples

**Alert: `ml-fraud-model-prediction-drift`**
```
FIRING: Fraud model positive prediction rate increased from 2.1% to 7.3%
Duration: 4 hours
Impact: Operations team overwhelmed with manual reviews
```
**Runbook:** Check if upstream data changed → If yes, classify as data drift and notify data eng. If no, check recent deploys → If deploy found, rollback. If neither, escalate to data science as potential concept drift.

**Alert: `ml-credit-model-data-drift`**
```
FIRING: Feature 'monthly_income' distribution PSI = 0.31 (threshold: 0.2)
Duration: 2 days (gradual)
Impact: No accuracy degradation detected yet
```
**Runbook:** Confirm with data engineering that source is correct → Check if business change explains shift (new customer segment?) → If accuracy still good, log and prepare retraining dataset. If accuracy dropping, escalate to P2.

**Alert: `ml-aml-model-serving-skew`**
```
FIRING: Feature 'transaction_velocity_24h' mean at serving (12.4) differs from training (45.7) by >10%
Triggered: 30 minutes after pipeline deploy v2.3.1
Impact: AML model missing suspicious patterns
```
**Runbook:** Immediate rollback of pipeline v2.3.1 → Compare feature computation logic between versions → Fix and add integration test → Redeploy with canary.

---

## 7. Key Takeaways for Your Role

1. **You don't need to fix the model** — you need to detect the problem, classify it, and route it correctly.
2. **Prediction drift is your first-line alert** — it doesn't require ground truth and fires fastest.
3. **Training-serving skew is YOUR territory** — it's a pipeline/infra bug, and your team owns infrastructure.
4. **Concept drift is the data science team's problem** — but you need to detect the symptom and escalate with evidence.
5. **The runbook pattern is: detect → classify drift type → respond appropriately.** Not all model problems need retraining.

---

## 8. Resources

- [Evidently AI Documentation](https://docs.evidentlyai.com/) — The tool you'll use in the lab; excellent drift detection library
- [Evidently: What is Data Drift?](https://www.evidentlyai.com/ml-in-production/data-drift) — Clear explanation with examples
- [Google ML Engineering Best Practices](https://developers.google.com/machine-learning/guides/rules-of-ml) — Rules of ML, very ops-friendly
- [Sculley et al. — Hidden Technical Debt in ML Systems](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) — The classic paper on ML system failures
- [NannyML: Concept Drift Guide](https://www.nannyml.com/blog/concept-drift-detection) — Good complement to Evidently
- [Made With ML: MLOps Course](https://madewithml.com/) — Full MLOps curriculum, good reference

---

## 9. Checklist

- [ ] I can define Accuracy, Precision, Recall, and F1 without looking them up
- [ ] I can explain when you'd optimize for Precision vs Recall (with a bank example)
- [ ] I can read a confusion matrix and identify which failure mode dominates
- [ ] I can name all 4 drift types and explain each in one sentence
- [ ] I can explain the detection timeline (what you see first vs last)
- [ ] I can map each drift type to a response action (retrain / rollback / investigate / fix)
- [ ] I've completed the drift detection lab notebook
- [ ] I've written my ML failure modes runbook (Milestone 1)
- [ ] I can explain training-serving skew as a pipeline bug (my team's domain)
- [ ] I can walk through the drift decision tree for a hypothetical incident

---

*Next week: Model deployment patterns (canary, shadow, blue-green) and how to build the serving infrastructure.*
