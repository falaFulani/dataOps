# Week 8: ML Observability

> **You already build SLO dashboards. This week, you add the ML row to the same dashboard — prediction quality, drift scores, and data freshness alongside your existing latency/error/saturation panels.**

## The Two-Layer Monitoring Model

You know monitoring. You've built Prometheus/Grafana stacks, defined SLOs, set up alerting that doesn't page at 3am for noise. That's Layer 1. What's new is Layer 2 — ML-specific signals that your existing stack won't catch.

| Layer | What It Catches | Your Familiarity |
|-------|----------------|-----------------|
| **Layer 1: Operational** | Latency, error rates, throughput, saturation, pod health | ✅ You own this already |
| **Layer 2: ML-Specific** | Drift, prediction quality, data freshness, feature distributions | 🆕 This is the new layer |

**Both layers use the same tools** (Prometheus + Grafana for collection and dashboards). The difference is *what* you instrument and *what* the alerts mean.

---

## The "Green Pipeline, Wrong Predictions" Problem

This is the core insight for this week. Traditional monitoring will tell you:

- ✅ Service is up (200 OK)
- ✅ Latency is within SLO (p99 < 200ms)
- ✅ No errors in logs
- ✅ CPU/memory normal
- ✅ All pods healthy

But the model is quietly returning garbage predictions because:

- The input data distribution shifted (customers changed behavior)
- A feature pipeline started producing stale data (data freshness issue)
- A model dependency changed silently upstream
- The training data no longer represents reality (concept drift)

**In ops terms:** Imagine a service that responds HTTP 200 with valid JSON, but the business logic silently returns wrong answers. No error. No crash. No latency spike. Just wrong. That's what ML model failure looks like.

Your existing monitoring stack is necessary but insufficient. You need both layers.

---

## ML Metrics to Instrument

These are the custom Prometheus metrics you'll add to your model service. The file `app/metrics.py` in this directory implements all of them.

### Operational Metrics (Layer 1 — Your Comfort Zone)

| Metric | Type | Purpose |
|--------|------|---------|
| `prediction_requests_total` | Counter | Total predictions served (by model version, predicted class) |
| `prediction_latency_seconds` | Histogram | Inference time distribution |
| `http_request_errors_total` | Counter | 4xx/5xx responses |
| `model_load_time_seconds` | Gauge | Time taken to load the model |

### ML-Specific Metrics (Layer 2 — The New Layer)

| Metric | Type | Purpose |
|--------|------|---------|
| `prediction_confidence` | Histogram | Distribution of confidence scores — drops signal degradation |
| `model_drift_score` | Gauge | Overall drift score from statistical tests |
| `data_quality_score` | Gauge | % of inputs passing quality checks |
| `feature_drift_detected` | Gauge | Per-feature drift indicators (0/1) |
| `prediction_distribution` | Histogram | Tracks which classes are being predicted — shift = something changed |
| `data_freshness_seconds` | Gauge | Age of the most recent training data |

### Why Each Metric Matters

**`prediction_confidence`** — If your model starts returning low-confidence predictions, it's uncertain. That's a leading indicator of drift. You can alert on this before accuracy actually drops.

**`model_drift_score`** — A single number (usually from a statistical test like KS or PSI) that says "how different is current input data from training data?" Think of it as a SLI for data relevance.

**`feature_drift_detected`** — Per-feature flag. When 3 out of 20 features drift, you know exactly which pipeline to investigate. This is your "which component is broken" signal.

**`data_quality_score`** — What percentage of incoming requests have valid, complete feature vectors? Missing values, out-of-range values, and schema violations all degrade quality silently.

**`prediction_distribution`** — If your model normally predicts 40% class A, 35% class B, 25% class C, and suddenly it's predicting 90% class A — something changed. This is your cheapest, fastest drift signal.

---

## Golden Signals for ML

You know the Google SRE golden signals. Here's the ML extension:

| Signal | Traditional (You Know This) | ML Addition (New) |
|--------|---------------------------|-------------------|
| **Latency** | Request duration p50/p95/p99 | Inference latency specifically (model computation time, not network) |
| **Traffic** | Requests per second | Predictions per second, broken down by model version |
| **Errors** | HTTP 5xx rate | + Prediction quality errors (low confidence, failed validations) |
| **Saturation** | CPU, memory, queue depth | + Model staleness (time since last retrain), feature pipeline lag |
| **— New —** | | |
| **Drift** | N/A | Data drift score, concept drift indicators |
| **Quality** | N/A | Prediction confidence, data quality rate |
| **Freshness** | N/A | Data age, feature freshness, model age |

The top 4 go on your existing dashboard. The bottom 3 are the new row.

---

## Architecture: Combined Observability Stack

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Grafana Dashboard                            │
│                                                                      │
│  ┌─────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Operational Panels         │  │  ML-Specific Panels            │ │
│  │  • Request rate             │  │  • Prediction distribution     │ │
│  │  • Latency p50/p95/p99     │  │  • Confidence histogram        │ │
│  │  • Error rate               │  │  • Drift score gauge           │ │
│  │  • Pod resources            │  │  • Data quality rate           │ │
│  │  • Saturation               │  │  • Feature drift indicators    │ │
│  └─────────────────────────────┘  └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ PromQL queries
                              │
┌──────────────────────────────────────────────────────────────────────┐
│                          Prometheus                                   │
│  • Scrapes /metrics from model service                               │
│  • Stores both operational AND ML metrics in the same TSDB           │
│  • Alertmanager rules for both layers                                │
└──────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ /metrics endpoint (Prometheus format)
                              │
┌──────────────────────────────────────────────────────────────────────┐
│                      Model Service (FastAPI)                          │
│                                                                      │
│  prometheus_client library exposes:                                   │
│  • Standard HTTP metrics (requests, latency, errors)                 │
│  • Custom ML metrics (confidence, drift, quality)                    │
│                                                                      │
│  On each prediction:                                                 │
│  1. Record latency (histogram)                                       │
│  2. Increment prediction counter (with labels)                       │
│  3. Observe confidence score (histogram)                             │
│  4. Check data quality (gauge)                                       │
│                                                                      │
│  On a schedule (background task or sidecar):                         │
│  5. Compute drift scores (gauge)                                     │
│  6. Update feature drift flags (gauge)                               │
│  7. Update data freshness (gauge)                                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Optional: Adding Evidently or Arize

For deeper ML monitoring (beyond what custom Prometheus metrics give you):

| Tool | What It Adds | When to Use |
|------|-------------|-------------|
| **Evidently AI** | Statistical drift reports, data quality reports, model performance dashboards | When you want automated drift detection with proper statistical tests |
| **Arize** | Embedding drift, slice-based performance, model comparison | When you have many models and need a managed platform |
| **WhyLabs** | Data profiling, anomaly detection on features | When data quality is the primary concern |

These tools complement Prometheus/Grafana — they don't replace it. Your operational layer stays in Prometheus. The ML-specific analysis layer can use these tools, and you can export their scores back to Prometheus as gauges.

---

## Mapping Table: Operational → ML Monitoring

This is the mental model for your transition. Every operational concept has an ML equivalent:

| Operational Concept (You Know) | ML Equivalent (Add This) |
|-------------------------------|--------------------------|
| Service uptime SLI | + Prediction quality SLI (% predictions above confidence threshold) |
| Error rate (5xx) | + Soft errors (low confidence, drift-affected predictions) |
| Latency p99 SLO | + Inference latency SLO (model computation, not just HTTP) |
| Throughput/RPS | + Predictions per model version (to detect routing issues) |
| Deploy canary → watch error rate | + Deploy canary → watch prediction distribution shift |
| PagerDuty alert: "service down" | + Alert: "drift score > threshold for 30min" |
| Runbook: "restart service" | + Runbook: "rollback model version or trigger retrain" |
| Dashboard: CPU, memory, network | + Dashboard row: drift, confidence, prediction distribution |
| Log-based debugging | + Prediction log analysis (what was predicted wrong?) |
| Synthetic monitoring (ping) | + Shadow predictions on known data (ongoing accuracy check) |

---

## Tools for This Week's Lab

| Tool | Role | Runs As |
|------|------|---------|
| **Prometheus** | Scrapes and stores all metrics (both layers) | Docker container |
| **Grafana** | Dashboard visualization (both layers, one dashboard) | Docker container |
| **prometheus_client (Python)** | Instruments the model service with custom metrics | Library in app |
| **Model Service** | FastAPI app with ML + operational metrics exposed | Docker container |

All four run locally via `docker-compose.yml` in this directory.

---

## Lab: Build the Combined Dashboard

### Quick Start

```bash
# 1. Verify prerequisites
chmod +x setup.sh && ./setup.sh

# 2. Start the observability stack
docker compose up -d

# 3. Access the services:
#    - Model service: http://localhost:8000
#    - Prometheus:    http://localhost:9090
#    - Grafana:       http://localhost:3000 (admin/admin)

# 4. Make some predictions to generate metrics:
for i in $(seq 1 20); do
  curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"features": [5.1, 3.5, 1.4, 0.2]}' > /dev/null
done

# 5. Open Grafana → "ML Observability" dashboard
#    See both layers side by side.
```

### What You'll See

After generating some traffic, the provisioned Grafana dashboard shows:

**Top row (Operational — familiar):**
- Request rate (req/s)
- Latency percentiles (p50, p95, p99)
- Error rate (%)
- Container resource usage

**Bottom row (ML — new):**
- Prediction class distribution (are predictions balanced?)
- Confidence score histogram (is the model certain?)
- Drift score gauge (is input data changing?)
- Data quality rate (are inputs valid?)

Same dashboard. Same alerting stack. New signals.

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This guide |
| `docker-compose.yml` | Full observability stack (Prometheus + Grafana + Model Service) |
| `prometheus/prometheus.yml` | Prometheus scrape configuration |
| `grafana/dashboards/ml-observability.json` | Pre-built Grafana dashboard (both layers) |
| `grafana/provisioning/datasources.yml` | Grafana datasource config (Prometheus) |
| `grafana/provisioning/dashboards.yml` | Grafana dashboard provisioning config |
| `app/metrics.py` | Custom Prometheus metrics instrumentation |
| `setup.sh` | Prerequisite verification script |

---

## Resources

| Resource | Why |
|----------|-----|
| [Prometheus Client Python](https://github.com/prometheus/client_python) | The library used in `app/metrics.py` |
| [Evidently AI Docs](https://docs.evidentlyai.com/) | Drift detection and ML monitoring |
| [Arize AI Platform](https://arize.com/) | Managed ML observability |
| [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) | Golden signals — you know this, reference for the ML extension |
| [NannyML — Estimated Performance](https://www.nannyml.com/) | Estimate model accuracy without ground truth labels |
| [ML Monitoring vs Traditional Monitoring (Chip Huyen)](https://huyenchip.com/2022/02/07/data-distribution-shifts-and-monitoring.html) | Excellent deep-dive on why traditional monitoring is insufficient |
| [Prometheus Best Practices — Metric Naming](https://prometheus.io/docs/practices/naming/) | For naming your custom ML metrics |

---

## Week 8 Checklist

- [ ] Read this README — internalize the two-layer model
- [ ] Review `app/metrics.py` — understand each custom metric and why it exists
- [ ] Run `setup.sh` to verify Docker is available
- [ ] Run `docker compose up -d` to start the stack
- [ ] Generate prediction traffic (use the curl loop above)
- [ ] Open Prometheus (`:9090`) — query `prediction_requests_total` and `prediction_confidence`
- [ ] Open Grafana (`:3000`) — explore the pre-built "ML Observability" dashboard
- [ ] Identify which panels are operational (Layer 1) vs ML-specific (Layer 2)
- [ ] Modify `app/metrics.py` to add a new custom metric (e.g., `model_age_seconds`)
- [ ] Think about: What SLOs would you define on the ML metrics? (That's next week)
- [ ] Think about: How would you alert on drift score without creating noise?
- [ ] Think about: Where does Evidently/Arize fit in your bank's existing Prometheus/Grafana stack?

---

## Key Takeaways

1. **Two layers, one stack.** Operational metrics and ML metrics live in the same Prometheus/Grafana. No separate tool needed for the basics.
2. **The silent failure mode.** ML models fail without errors. Drift and quality metrics are your smoke detectors for this.
3. **Confidence is your leading indicator.** Dropping confidence scores predict accuracy problems before they manifest.
4. **Prediction distribution is free and powerful.** If the distribution of outputs changes, something changed in the inputs. Cheapest signal you can add.
5. **You're not starting from scratch.** You're adding 5-6 custom metrics to a service you already know how to monitor. That's it.
