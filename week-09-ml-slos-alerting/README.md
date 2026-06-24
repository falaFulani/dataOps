# Week 9 — ML SLOs & Alerting Frameworks

**Time budget:** 8–10 hours  
**Goal:** Define what "good" looks like for an ML system and build alerting that catches real problems — drift burn-rate, not raw feature noise.  
**Key insight:** This week IS the job description. You already know how to define SLOs, build error budgets, write Prometheus alerting rules, and manage on-call. Now you apply those exact frameworks to a new signal type: ML prediction quality, drift, and data freshness.

---

## Concepts to Cover

### 1. Defining SLOs for ML Systems

In traditional services, SLOs are straightforward: availability, latency, throughput. ML systems have those **plus** a second layer that's invisible to infrastructure monitoring:

```
┌─────────────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE SLOs (you already have these)                   │
│  • Service uptime: 99.9%                                        │
│  • Inference latency: p99 < 200ms                               │
│  • Throughput: handle 1000 req/s                                 │
├─────────────────────────────────────────────────────────────────┤
│  ML-SPECIFIC SLOs (new territory)                               │
│  • Prediction quality: accuracy > 0.90 on holdout               │
│  • Data freshness: training data < 30 days old                  │
│  • Drift score: PSI/KS < 0.2 for all monitored features        │
│  • Prediction distribution: output distribution shift < 0.15    │
└─────────────────────────────────────────────────────────────────┘
```

**Two categories of ML SLOs:**

| Category | What it measures | Example |
|----------|-----------------|---------|
| **Availability SLOs** | Can the model serve predictions? | 99.9% uptime, p99 < 200ms |
| **Prediction-quality SLOs** | Are the predictions any good? | Accuracy > 0.90, drift < 0.2 |

The dangerous insight: **a model can be 100% available and completely wrong.** Infrastructure SLOs won't catch a model silently returning garbage predictions. That's why you need both layers.

### 2. Error Budgets for Models

You know error budgets: if your SLO is 99.9% availability over 30 days, you have ~43 minutes of allowed downtime. Spend it on deploys, experiments, maintenance. Burn it all? Stop shipping features and focus on reliability.

**For ML systems, "burning" the error budget looks different:**

| SLO Type | What "burning budget" means | How it accumulates |
|----------|----------------------------|-------------------|
| Availability | Service downtime | Minutes of outage |
| Latency | Requests exceeding p99 target | % of slow requests |
| Prediction quality | Accuracy below target | Hours below accuracy threshold |
| Data freshness | Training data age exceeds target | Hours past freshness deadline |
| Drift | Drift score exceeds threshold | Time spent above drift threshold |

**Example: Prediction Quality Error Budget**

- SLO: Model accuracy > 0.90 (measured on holdout set, evaluated hourly)
- Window: 30 days = 720 hours
- Budget: 10% of hours can be below threshold = 72 hours
- Current burn: Accuracy dropped to 0.87 for 18 hours = consumed 25% of budget

**The error budget policy for ML:**

| Budget remaining | Action |
|-----------------|--------|
| > 50% | Ship new features, experiment with model changes |
| 25–50% | Investigate drift, prioritize retraining pipeline improvements |
| < 25% | Stop experiments. Focus on model reliability: retrain, rollback, or fix data |
| 0% (exhausted) | Incident. Rollback to last-known-good model. Postmortem required. |

### 3. Alerting on Drift Burn-Rate, Not Noise

This is where your multi-window multi-burn-rate (MWMBR) experience directly applies. The problem in ML monitoring:

**Raw drift scores are noisy.** A single feature spiking for 5 minutes isn't an incident — it might be a batch of unusual-but-valid data. You don't page on a single 500 error; you page on error *rate* sustained over a window. Same logic.

**Apply multi-window multi-burn-rate to drift:**

```
# Traditional MWMBR (you know this):
# Alert if 14.4x burn rate over 1h AND 6x burn rate over 6h

# ML drift MWMBR equivalent:
# Alert if drift score is 3x threshold for 1h AND 1.5x threshold for 6h
# This catches sustained drift, not noise spikes
```

**Burn-rate windows for ML signals:**

| Severity | Short window | Long window | Burn rate | Action |
|----------|-------------|-------------|-----------|--------|
| Page (critical) | 5 min | 1 hour | 14.4x | Investigate immediately, consider rollback |
| Ticket (warning) | 30 min | 6 hours | 6x | Investigate within shift |
| Low | 2 hours | 3 days | 1x | Track, discuss in team review |

**The key translation:** In infrastructure, burn-rate tells you "at this rate, you'll exhaust your error budget in N hours." In ML, it tells you "at this drift rate, your model will be dangerously inaccurate in N hours."

### 4. Avoiding Alert Fatigue in ML Monitoring

ML systems generate MORE telemetry than traditional services (every feature is a metric, every prediction is a data point). Without discipline, your team will drown in noise.

**Apply the same principles you already use:**

| Anti-fatigue principle | Traditional application | ML application |
|----------------------|----------------------|---------------|
| Alert on symptoms, not causes | Page on user-facing error rate, not CPU | Page on prediction quality drop, not individual feature drift |
| Multi-window validation | Require sustained signal before paging | Drift must persist across windows to page |
| Severity tiers | Page vs ticket vs dashboard | Critical drift → page; moderate → ticket; low → dashboard |
| Actionable alerts only | Every page has a clear runbook action | Every ML alert maps to: retrain / rollback / investigate data |
| Aggregate, don't enumerate | One alert for "cluster unhealthy" not per-node | One alert for "model degraded" not per-feature |
| Suppress during known events | Silence during maintenance | Suppress drift alerts during retraining windows |

**ML-specific anti-fatigue rules:**

1. **Never page on a single feature drifting.** Require N features or composite score.
2. **Separate leading indicators from pages.** Drift is a leading indicator → dashboard/ticket. Prediction quality drop is a lagging indicator → page.
3. **Suppress during retraining.** Model metrics will fluctuate during retrain; don't alert.
4. **Use holdout evaluation, not live accuracy** (you rarely have real-time labels).
5. **Business hours for non-critical.** Drift tickets go to the team during business hours, not 3 AM.

### 5. SLO Hierarchy

ML systems have a layered SLO structure. Each layer depends on the one below it:

```
┌─────────────────────────────────────────────────┐
│          BUSINESS SLOs                          │
│  "Fraud detection rate > 95%"                   │
│  "Customer churn prediction saves $X/quarter"   │
├─────────────────────────────────────────────────┤
│          MODEL SLOs                             │
│  "Accuracy > 0.90 on holdout"                   │
│  "Drift score < 0.2"                            │
│  "Training data < 30 days old"                  │
├─────────────────────────────────────────────────┤
│          SERVICE SLOs                           │
│  "p99 latency < 200ms"                          │
│  "Throughput > 1000 req/s"                      │
│  "Error rate < 0.1%"                            │
├─────────────────────────────────────────────────┤
│          INFRASTRUCTURE SLOs                    │
│  "K8s cluster availability > 99.99%"            │
│  "GPU utilization < 80%"                        │
│  "Storage IOPS within limits"                   │
└─────────────────────────────────────────────────┘
```

**Why the hierarchy matters:**
- Infrastructure failure cascades up → all layers breach
- Model failure only affects model + business layers → service stays "healthy"
- Business SLOs are the ultimate truth, but they're lagging and hard to measure in real-time
- Your job: catch problems at the model/service layer before they reach business impact

**Alerting priority follows the hierarchy:**
- Infrastructure alerts: page the platform team (you)
- Service alerts: page the ML service on-call
- Model alerts: ticket/page the ML engineering team
- Business alerts: escalate to product/business stakeholders

### 6. Leading vs Lagging Indicators

This distinction determines your alerting strategy:

| Indicator type | What it tells you | Response time | Examples |
|---------------|-------------------|---------------|---------|
| **Leading** | Something *will* go wrong | Hours to days of warning | Drift score rising, confidence distribution shifting, data freshness approaching limit |
| **Lagging** | Something *has* gone wrong | Already impacting users | Accuracy dropped, false positive rate spiked, business metrics declining |

**Alerting strategy by indicator type:**

```
LEADING INDICATORS (drift, confidence, freshness)
  → Dashboard widgets (always visible)
  → Warning tickets when threshold approaching
  → Page ONLY if burn-rate suggests imminent breach

LAGGING INDICATORS (accuracy drop, business metric decline)
  → Page immediately (damage is happening now)
  → Trigger rollback decision tree
  → Post-incident: why didn't leading indicators catch this earlier?
```

**The ideal state:** Your leading indicator alerts give you enough warning to retrain or rollback BEFORE lagging indicators ever fire. If you're always catching problems via lagging indicators, your leading indicator thresholds need tightening.

### 7. Mapping Table: Traditional SLO Concepts → ML SLO Equivalents

| Traditional SLO/Alerting Concept | ML Equivalent | Notes |
|----------------------------------|---------------|-------|
| Service availability (uptime) | Model service availability | Identical — your model endpoint is a service |
| Request latency SLO | Inference latency SLO | Same, but watch for model size impacts |
| Error rate | Prediction error rate (where labels available) | Labels are delayed in ML; use proxy metrics |
| Error budget (minutes of downtime) | Error budget (hours of degraded accuracy) | Same math, different unit |
| Burn rate | Drift burn rate | How fast you're consuming quality budget |
| Multi-window multi-burn-rate | Multi-window on drift + quality metrics | Directly applicable |
| Canary analysis (error rate on canary vs baseline) | Shadow scoring (new model vs production) | Statistical comparison of two populations |
| Health check endpoint | Health check + model-loaded check | Add "model version served" to health response |
| Dependency SLO (DB latency affects service SLO) | Feature store SLO (stale features affect model SLO) | New dependency to track |
| SLO burn alert → page on-call | Drift burn alert → page ML on-call | Same routing, new signal |
| Post-incident: "what caused the 500s?" | Post-incident: "what caused the accuracy drop?" | Root cause is often data, not code |
| Deployment rollback | Model rollback (revert to previous version) | Same pattern via model registry |
| Error budget policy: "freeze deploys" | Error budget policy: "freeze experiments, retrain" | Same governance, different action |

---

## Hands-on Lab

### Step 1: Review the SLO Definitions

Open `slo-definitions.yml` and study the 5 SLOs defined for our model service. Notice how each one has:
- An objective (the target)
- A measurement method (how you'd actually compute it)
- An error budget (how much violation is acceptable)
- Alert thresholds (when to warn vs page)
- Consequences (what happens on breach)

### Step 2: Review the Alerting Rules

Open `alerting-rules.yml` — these are Prometheus alerting rules in the `PrometheusRule` CRD format you'd apply to a k8s cluster with the Prometheus Operator. Notice:
- Multi-window burn-rate alerts for availability and latency
- Drift-specific alerts with warn/critical tiers
- Prediction distribution shift detection
- Model staleness alerts

### Step 3: Run the Error Budget Calculator

```bash
# Set up
chmod +x setup.sh
./setup.sh
source venv/bin/activate

# Run the calculator with defaults (90% accuracy SLO, 30-day window)
python error-budget-calculator.py

# Try different scenarios
python error-budget-calculator.py --slo-target 0.95 --window-days 7
python error-budget-calculator.py --slo-target 0.999 --window-days 30
python error-budget-calculator.py --slo-target 0.90 --window-days 30 --current-value 0.87 --breach-hours 18
```

### Step 4: Review the Runbook

Open `alert-runbook.md` — this is the operational document you'd hand to an ML on-call engineer. Notice how each alert has:
- Clear severity and description
- Step-by-step investigation procedure
- Decision trees for resolution
- Escalation paths

### Step 5: Apply to Your Context

Think about your bank's model services:
- Which SLOs from `slo-definitions.yml` would you adopt as-is vs customize?
- Which alerts would you add or remove?
- How would the escalation paths differ given your org structure?
- What regulatory requirements affect your error budget policy?

---

## Key Takeaways for Your Role

1. **You already know this.** SLOs, error budgets, burn-rate alerting, runbooks — this is your domain. The new part is the *signals*, not the *framework*.
2. **ML adds a "silent failure" layer.** A model can be up, fast, and wrong. Your alerting must cover prediction quality, not just infrastructure.
3. **Drift is a leading indicator, not an alert trigger.** Alert on drift *burn-rate* sustained over windows, not instantaneous spikes.
4. **Error budget policy drives team behavior.** When the ML error budget is exhausted, the team retrains/rollbacks instead of shipping new features. Same governance, new actions.
5. **The hierarchy matters for escalation.** Infrastructure issues → you. Model issues → ML team. Business impact → product. Wire this into PagerDuty routing.

---

## Resources

- 📚 [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- 📚 [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) — the MWMBR pattern reference
- 📚 [Chip Huyen — Monitoring ML Systems in Production](https://huyenchip.com/2022/02/07/data-distribution-shifts-and-monitoring.html)
- 📚 [Evidently AI — ML Monitoring Best Practices](https://www.evidentlyai.com/ml-in-production/ml-monitoring-metrics)
- 📚 [NannyML — Estimating Model Performance Without Labels](https://nannyml.readthedocs.io/en/stable/)
- 📚 [Arize AI — ML Observability Concepts](https://docs.arize.com/arize/)
- 📚 [OpenSLO Specification](https://openslo.com/) — standardized SLO-as-code format

---

## Checklist

- [ ] Read through all concepts above — confirm the mapping from your existing SLO knowledge to ML signals
- [ ] Review `slo-definitions.yml` — could you define these for a model at your bank?
- [ ] Review `alerting-rules.yml` — identify the multi-window burn-rate pattern
- [ ] Run `error-budget-calculator.py` with different scenarios
- [ ] Read `alert-runbook.md` — compare to your existing runbooks
- [ ] Write 3–5 sentences: "What's different about ML alerting vs what I do today?"
- [ ] Draft one SLO + error budget policy for a model at your bank (even hypothetical)
- [ ] Identify which leading indicators you'd put on a dashboard vs which lagging indicators you'd page on
- [ ] Sketch an escalation path: drift detected → who gets notified → at what threshold → what action
