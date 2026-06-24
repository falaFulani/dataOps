# ML Model Alert Runbook

**Service:** Fraud Detection Model  
**Team:** ML Platform / ML Engineering  
**Last updated:** 2024-01-15  
**Owner:** ML Platform On-Call

---

## How to Use This Runbook

Each alert section contains:
1. **Alert name** — matches the Prometheus alert name exactly
2. **Description** — what the alert means in plain language
3. **Severity** — critical (page) or warning (ticket)
4. **Investigation steps** — ordered checklist to diagnose root cause
5. **Resolution actions** — what to do once you've identified the problem
6. **Escalation path** — who to involve and when
7. **Decision tree** — flowchart for common scenarios

---

## Table of Contents

1. [Feature Drift Alerts](#1-feature-drift-alerts)
2. [Prediction Quality Alerts](#2-prediction-quality-alerts)
3. [Model Staleness Alerts](#3-model-staleness-alerts)
4. [Data Quality Alerts](#4-data-quality-alerts)
5. [Prediction Distribution Shift Alerts](#5-prediction-distribution-shift-alerts)
6. [Escalation Matrix](#6-escalation-matrix)

---

## 1. Feature Drift Alerts

### ModelFeatureDriftWarning

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **SLO** | feature-drift-score |
| **Meaning** | One or more features have drifted beyond threshold (PSI/KS > 0.2) for 2+ hours |

**Why this matters:** Feature drift is a leading indicator. If input data distributions shift away from what the model was trained on, prediction quality will degrade — but it hasn't yet. You have time to investigate and act.

#### Investigation Steps

1. **Identify the drifting feature(s)**
   ```
   # Check which features are above threshold
   max(feature_drift_score{model="fraud-detection"}) by (feature_name)
   ```

2. **Check the drift timeline**
   - When did the drift start? (Grafana: ML Drift dashboard)
   - Was the onset sudden (pipeline change) or gradual (organic shift)?

3. **Correlate with upstream changes**
   - Any recent deployments to upstream data pipelines?
   - Any changes to the feature store?
   - Any known business events (new product launch, marketing campaign)?

4. **Assess drift severity**
   - Is it a single feature or multiple?
   - How far above threshold? (0.21 vs 0.5 are very different situations)
   - Is the feature high-importance or low-importance to the model?

5. **Check prediction quality impact**
   ```
   # Has accuracy dropped yet?
   model_accuracy_score{model="fraud-detection", dataset="holdout"}
   ```

#### Resolution Actions

| Root Cause | Action |
|-----------|--------|
| Upstream pipeline change (bug) | Revert pipeline change, notify upstream team |
| Upstream pipeline change (intentional) | Retrain model on new distribution |
| Seasonal/organic shift | Schedule retraining if accuracy impacted |
| New product/feature launched | Retrain with new data; update reference distribution |
| False alarm (transient spike) | Close ticket; monitor. Adjust threshold if recurring |

#### Decision Tree

```
Drift detected
├── Is accuracy already impacted?
│   ├── YES → Escalate to ModelPredictionQualityCritical response
│   └── NO → Continue investigation
│       ├── Is drift due to upstream bug?
│       │   ├── YES → Revert upstream change. Drift should resolve.
│       │   └── NO → Is drift expected (seasonal, new product)?
│       │       ├── YES → Schedule retraining within 48h
│       │       └── NO → Investigate further. Monitor for 24h.
│       │           └── Still drifting after 24h? → Trigger retraining.
```

---

### ModelFeatureDriftCritical

| Field | Value |
|-------|-------|
| **Severity** | Critical (page) |
| **Routes to** | ML Engineering On-Call |
| **SLO** | feature-drift-score |
| **Meaning** | 3+ features drifting simultaneously OR single feature with extreme drift (>0.4) |

**Why this matters:** Multiple features drifting at once indicates a systemic upstream issue — not a single feature behaving oddly. The entire input distribution may have shifted. High probability of imminent prediction quality degradation.

#### Investigation Steps

1. **Determine scope immediately**
   ```
   # How many features are drifting? Which ones?
   count(feature_drift_score{model="fraud-detection"} > 0.2)
   topk(10, feature_drift_score{model="fraud-detection"})
   ```

2. **Check data pipeline health**
   - Is the feature store serving stale data?
   - Are upstream ETL jobs failing or delayed?
   - Any schema changes in source systems?

3. **Check for deployment correlation**
   - When did drift start? Cross-reference with deployment logs.
   - Was there a feature store update, pipeline deploy, or infra change?

4. **Verify model is still serving predictions**
   - Is the model returning predictions (not errors)?
   - Are predictions landing within expected ranges?

5. **Assess business impact**
   - Is this a model that blocks transactions (synchronous)?
   - What's the blast radius if predictions are wrong?

#### Resolution Actions

1. **If caused by data pipeline failure:**
   - Fix/restart pipeline
   - Backfill missing data if needed
   - Verify drift resolves after fix

2. **If caused by legitimate distribution shift:**
   - Trigger immediate retraining on fresh data
   - Monitor retrained model's validation metrics
   - Update reference distribution after retrain

3. **If accuracy is already degraded:**
   - Rollback to last-known-good model version
   - Trigger retraining in parallel
   - Notify business stakeholders of potential impact window

#### Escalation

- If drift correlates with data pipeline failure → page Data Engineering on-call
- If unable to identify root cause within 30 minutes → escalate to ML Platform Lead
- If model accuracy has dropped below 0.85 → declare incident, invoke incident commander

---

## 2. Prediction Quality Alerts

### ModelPredictionQualityWarning

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **SLO** | model-prediction-quality |
| **Meaning** | Model accuracy on holdout set dropped below 0.90 for 6+ consecutive hours |

#### Investigation Steps

1. **Confirm the accuracy drop is real**
   - Check holdout evaluation logs — is the evaluation pipeline healthy?
   - Is the holdout dataset up-to-date and representative?
   - Could this be a labeling issue (labels arriving late or incorrect)?

2. **Check for preceding drift**
   - Were there drift warnings before this accuracy drop?
   - If yes: the drift led to this. Retraining should help.
   - If no: possible concept drift (relationship between features and target changed)

3. **Review model version**
   - Which model version is serving? When was it trained?
   - Was there a recent model deployment that could have introduced this?

4. **Segment the accuracy drop**
   - Is accuracy down across all segments, or specific cohorts?
   - Specific cohort → data issue in that segment
   - All segments → systemic model degradation

#### Resolution Actions

| Situation | Action |
|----------|--------|
| Drift preceded accuracy drop | Retrain on fresh data |
| No drift, gradual decline | Likely concept drift — retrain with recent data + evaluate new features |
| Sudden drop after deployment | Rollback to previous model version |
| Holdout evaluation issue | Fix evaluation pipeline; accuracy may be fine |
| Seasonal pattern | Assess if model needs seasonal variants |

---

### ModelPredictionQualityCritical

| Field | Value |
|-------|-------|
| **Severity** | Critical (page) |
| **Routes to** | ML Engineering On-Call + ML Platform Lead |
| **SLO** | model-prediction-quality |
| **Meaning** | Accuracy below 0.90 for 24+ hours OR dropped below 0.85 at any point |

**This is a lagging indicator — damage is already happening.**

#### Investigation Steps

1. **Immediate assessment (first 5 minutes)**
   - What is the current accuracy? How long has it been below threshold?
   - Is the model still serving predictions? (Not failing, just wrong)
   - What model version is currently deployed?

2. **Determine if rollback is needed (5-15 minute decision)**
   - Is accuracy below 0.85? → Strong candidate for immediate rollback
   - Is there a last-known-good model version available?
   - What's the business impact of wrong predictions right now?

3. **Root cause investigation (parallel with mitigation)**
   - Follow the drift investigation steps above
   - Check model serving infrastructure — could be serving wrong version
   - Check feature pipeline — could be feeding stale/wrong features

#### Resolution Actions

**Priority 1: Mitigate**
```
# Rollback to last-known-good model
kubectl set image deployment/fraud-model \
  model=registry.internal/fraud-model:v2.3.1-stable

# OR: switch to rule-based fallback if no good model version exists
kubectl apply -f fallback-rules-deployment.yml
```

**Priority 2: Diagnose**
- Root cause investigation continues after mitigation
- Identify whether this is data drift, concept drift, or infrastructure issue

**Priority 3: Recover**
- Retrain model on fresh data (if drift/staleness)
- Fix pipeline and redeploy (if infrastructure)
- Validate new model meets SLO before promotion to production

#### Escalation

- 0-15 min: ML Engineering On-Call owns
- 15 min: If no clear path to resolution → ML Platform Lead
- 30 min: If business-critical model (fraud) → notify Business Stakeholder
- 60 min: If unresolved → Incident Commander, full incident process

---

## 3. Model Staleness Alerts

### ModelStalenessWarning

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **SLO** | training-data-freshness |
| **Meaning** | Model was last trained 25+ days ago (5 days until SLO breach) |

#### Investigation Steps

1. **Check retraining pipeline status**
   - Is the scheduled retraining pipeline enabled and healthy?
   - Was the last scheduled run successful? If not, why did it fail?
   - Is fresh training data available?

2. **Check for blocked dependencies**
   - Is the training data pipeline delivering fresh labeled data?
   - Are there resource constraints blocking training (GPU quota)?
   - Is there a pending model validation that's blocking promotion?

3. **Verify the schedule is correct**
   - What's the configured retraining frequency? (Should be < 30 days)
   - Was the schedule accidentally disabled or modified?

#### Resolution Actions

| Root Cause | Action |
|-----------|--------|
| Pipeline disabled/misconfigured | Fix config, trigger manual run |
| Pipeline failing (infra issue) | Fix infrastructure, trigger manual run |
| No fresh training data available | Escalate to Data Engineering — data pipeline may be broken |
| Model validation failing (new model worse) | Investigate why new model is worse; may need feature engineering |
| GPU/resource quota exhausted | Request quota increase or schedule during off-peak |

---

### ModelStalenessCritical / ModelStalenessBreach

| Field | Value |
|-------|-------|
| **Severity** | Critical (page) |
| **Routes to** | ML Platform On-Call + ML Engineering Lead |
| **SLO** | training-data-freshness |
| **Meaning** | 28+ days since training (2 days to breach) or 30+ days (SLO breached, compliance risk) |

#### Investigation Steps

1. **Same as warning**, but with urgency
2. **If breach (30+ days):** Immediately notify compliance team

#### Resolution Actions

**If 28 days (critical, not yet breached):**
1. Trigger manual retraining immediately
2. Monitor training run to completion
3. Fast-track model validation (expedited review)
4. Deploy retrained model as soon as validation passes

**If 30+ days (SLO breached):**
1. Declare incident
2. Trigger retraining
3. Notify compliance of temporary breach + expected resolution time
4. Document risk acceptance if retraining will take additional time
5. Evaluate switching to rule-based fallback if retraining timeline is unclear
6. Postmortem required — why did the pipeline stay broken for 30 days?

#### Escalation

- Immediate: ML Platform Lead + ML Engineering Lead
- If regulatory model: Compliance Officer within 4 hours
- If unable to retrain within 48 hours: VP Engineering

---

## 4. Data Quality Alerts

### DataQualityNullRateHigh

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **Meaning** | >5% of prediction requests contain null values in monitored features |

#### Investigation Steps

1. **Identify which features have nulls**
   ```
   topk(5, rate(feature_null_count_total{model="fraud-detection"}[15m])) by (feature_name)
   ```

2. **Determine if this is new or chronic**
   - Was null rate stable before? When did it increase?
   - Cross-reference with upstream deployments

3. **Check data source health**
   - Is the feature store returning nulls? (Feature store issue)
   - Is the source system not providing data? (Upstream issue)
   - Is there a join failure in the feature pipeline? (Pipeline bug)

4. **Assess impact**
   - How does the model handle nulls? (Imputation? Default value? Error?)
   - Are predictions still serving? Are they degraded?

#### Resolution Actions

| Root Cause | Action |
|-----------|--------|
| Feature store serving stale cache | Restart/refresh feature store |
| Upstream source system down | Escalate to source system team |
| Pipeline join failure | Fix pipeline logic |
| Schema change in source | Update pipeline to handle new schema |

---

### DataQualitySchemaViolation

| Field | Value |
|-------|-------|
| **Severity** | Critical (page) |
| **Routes to** | ML Engineering On-Call |
| **Meaning** | Model is receiving features that violate expected schema (wrong types, out-of-range) |

**Why this is critical:** Schema violations mean the model is receiving fundamentally wrong data. Predictions are likely garbage, even if the model isn't throwing errors (it may silently produce bad outputs).

#### Investigation Steps

1. **Identify the violation type**
   - Wrong data type? (String where number expected)
   - Out of expected range? (Negative amounts, future dates)
   - Unexpected categorical values? (New category model hasn't seen)

2. **Determine source**
   - Recent upstream pipeline deployment?
   - Source system schema change?
   - Feature store bug?

3. **Assess prediction impact**
   - Is the model still serving? What are predictions looking like?
   - Are there downstream consumers relying on these predictions?

#### Resolution Actions

1. **Immediate:** If predictions are unreliable, switch to fallback (rule-based)
2. **Fix:** Identify and revert the upstream change causing schema violations
3. **Validate:** Confirm schema violations stop after fix
4. **Prevent:** Add schema validation to the feature pipeline (block bad data before it reaches the model)

---

### DataQualityDistributionAnomaly

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **Meaning** | 2+ features showing extreme distribution anomalies (>5 std devs from reference) |

#### Investigation Steps

1. **Distinguish from normal drift**
   - Normal drift: gradual shift over days/weeks
   - Anomaly: sudden, extreme shift (>5 sigma) → likely a bug, not organic change

2. **Check for data pipeline issues**
   - Unit conversion errors (cents vs dollars, seconds vs milliseconds)
   - Duplicate data inflating counts
   - Missing joins filling with defaults

3. **Cross-reference with other alerts**
   - Are drift alerts also firing? (Expected — anomaly causes drift)
   - Any schema violations? (Related root cause)

#### Resolution Actions

- Trace the anomaly to its source system/pipeline
- Fix the data issue
- Determine if predictions during the anomaly window were impacted
- Consider reprocessing/backfilling if predictions were wrong

---

## 5. Prediction Distribution Shift Alerts

### PredictionDistributionShiftWarning

| Field | Value |
|-------|-------|
| **Severity** | Warning (ticket) |
| **Routes to** | ML Engineering (business hours) |
| **Meaning** | Model prediction outputs have shifted >2 standard deviations from baseline for 2+ hours |

#### Investigation Steps

1. **Check prediction distribution**
   - What's the current mean prediction score vs baseline?
   - Is the model predicting "fraud" more or less often than expected?

2. **Determine if input or model issue**
   - Are drift alerts also firing? → Input data changed → model responding normally to new data
   - No drift? → Possible model issue (wrong version deployed, model corruption)

3. **Verify model version**
   - Is the expected model version serving?
   - Was there a recent deployment or rollback?

#### Resolution Actions

| Root Cause | Action |
|-----------|--------|
| Input drift causing prediction shift | Normal — model responding to data. Consider retraining. |
| Wrong model version deployed | Rollback to correct version |
| Legitimate shift in fraud patterns | Validate with domain experts; may be correct behavior |
| Model corruption/serving bug | Rollback, investigate serving infrastructure |

---

### PredictionDistributionShiftCritical

| Field | Value |
|-------|-------|
| **Severity** | Critical (page) |
| **Routes to** | ML Engineering On-Call |
| **Meaning** | Prediction output shifted >4 standard deviations — extreme anomaly |

**This is an emergency.** A 4-sigma shift in prediction output means the model is behaving fundamentally differently than baseline. High probability of wrong predictions impacting customers.

#### Immediate Actions (first 5 minutes)

1. Verify model version: `kubectl describe deployment/fraud-model | grep Image`
2. Check recent deployments: any model or config changes in last hour?
3. Check prediction samples: are outputs reasonable or clearly wrong?
4. **If predictions are clearly wrong:** Rollback immediately. Investigate after.

#### Decision Tree

```
Prediction shift > 4 sigma
├── Was there a recent model deployment?
│   ├── YES → Rollback immediately. Investigate the new model.
│   └── NO → Check feature pipeline
│       ├── Feature pipeline broken? → Fix pipeline, predictions should normalize
│       └── Pipeline healthy? → Check model serving infrastructure
│           ├── GPU/memory issues? → Restart/scale model pods
│           └── Unknown → Rollback to last-known-good. Investigate.
```

---

## 6. Escalation Matrix

### Severity Levels and Response Times

| Severity | Response Time | Who's Paged | Decision Authority |
|----------|--------------|-------------|-------------------|
| Warning (ticket) | Next business day | Nobody (ticket created) | ML Engineer on rotation |
| Critical (page) | 15 minutes | ML Engineering On-Call | On-Call Engineer |
| Incident | Immediate | On-Call + Incident Commander | Incident Commander |

### Escalation Paths by Alert Category

| Alert Category | First Responder | Escalation 1 (15 min) | Escalation 2 (30 min) | Escalation 3 (60 min) |
|---------------|-----------------|----------------------|----------------------|----------------------|
| Drift | ML Engineer | ML Platform Lead | ML Engineering Manager | VP Engineering |
| Prediction Quality | ML Engineer On-Call | ML Platform Lead | Business Stakeholder | VP Engineering |
| Staleness | ML Engineer | ML Platform Lead | Compliance (if regulatory) | VP Engineering |
| Data Quality | ML Engineer | Data Engineering Lead | ML Platform Lead | VP Engineering |
| Prediction Shift | ML Engineer On-Call | ML Platform Lead | Business Stakeholder | Incident Commander |

### When to Declare an Incident

Declare a formal incident when ANY of the following are true:
- Model accuracy below 0.85 and not recovering
- Prediction distribution shift > 4 sigma for > 30 minutes
- Model staleness SLO breached (30+ days) on regulatory model
- Multiple alert categories firing simultaneously (systemic failure)
- Unable to identify root cause within 30 minutes of critical alert
- Business stakeholder reports downstream impact

### Incident Roles (ML-specific)

| Role | Responsibility |
|------|---------------|
| **Incident Commander** | Coordinates response, communicates to stakeholders |
| **ML Engineer** | Investigates model behavior, executes rollback/retrain |
| **Data Engineer** | Investigates data pipeline health, fixes upstream issues |
| **Platform Engineer** | Investigates serving infrastructure, resource issues |
| **Business Liaison** | Assesses business impact, communicates to affected teams |

---

## Appendix: Quick Reference

### Rollback Procedure

```bash
# 1. Identify last-known-good model version
mlflow models list --name fraud-detection --stages Production,Archived

# 2. Deploy previous version
kubectl set image deployment/fraud-model \
  model=registry.internal/fraud-model:<PREVIOUS_VERSION>

# 3. Verify rollback
curl -X POST http://fraud-model.internal/predict \
  -d '{"features": <test_payload>}'

# 4. Confirm metrics recovering
# Check Grafana ML SLOs dashboard
```

### Retraining Trigger Procedure

```bash
# 1. Trigger manual retraining pipeline
prefect deployment run fraud-model-training/production --param force=true

# 2. Monitor training progress
prefect flow-run ls --flow-name fraud-model-training --limit 1

# 3. Validate new model (automated in pipeline, but verify)
mlflow models get-latest-versions fraud-detection --stages Staging

# 4. Promote to production (after validation passes)
mlflow models transition-stage fraud-detection <VERSION> Production
```

### Useful Prometheus Queries

```promql
# Current model accuracy
model_accuracy_score{model="fraud-detection", dataset="holdout"}

# Drift scores for all features
feature_drift_score{model="fraud-detection"}

# Model age in days
(time() - model_last_training_timestamp{model="fraud-detection"}) / 86400

# Error budget remaining (availability)
1 - (
  sum(rate(http_requests_total{service="fraud-model", code!~"2.."}[30d]))
  /
  sum(rate(http_requests_total{service="fraud-model", code!~"4.."}[30d]))
) / 0.001

# Prediction score distribution (current vs baseline)
histogram_quantile(0.5, rate(prediction_score_bucket{model="fraud-detection"}[1h]))
```
