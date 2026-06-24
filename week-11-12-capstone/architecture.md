# Architecture Document — MLOps Capstone

This document describes the architecture of your end-to-end MLOps system.
Fill in each section based on your actual implementation.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        ┌─────────────────────┐                              │
│                        │   Data Source        │                              │
│                        │   (CSV / API / DB)   │                              │
│                        └──────────┬───────────┘                              │
│                                   │                                          │
│                                   ▼                                          │
│                        ┌─────────────────────┐                              │
│                        │  Data Validation     │                              │
│                        │  (schema + quality)  │                              │
│                        └──────────┬───────────┘                              │
│                                   │                                          │
│                                   ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Training Pipeline (Prefect)                       │    │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────┐   │    │
│  │  │ Validate │──▶│  Train   │──▶│ Evaluate │──▶│ Register in   │   │    │
│  │  │  Data    │   │  Model   │   │  Model   │   │ MLflow        │   │    │
│  │  └──────────┘   └──────────┘   └──────────┘   └───────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                       │                      │
│                                                       ▼                      │
│                                            ┌─────────────────────┐          │
│                                            │  Model Registry     │          │
│                                            │  (MLflow)           │          │
│                                            │  staging → prod     │          │
│                                            └──────────┬──────────┘          │
│                                                       │                      │
│                                                       ▼                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Serving Layer                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────┐   │    │
│  │  │  FastAPI Application (containerized)                         │   │    │
│  │  │  ├── GET  /health       → liveness + readiness              │   │    │
│  │  │  ├── POST /predict      → model inference                   │   │    │
│  │  │  └── GET  /metrics      → Prometheus metrics                │   │    │
│  │  └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                     │    │
│  │  Deployed on Kubernetes:                                            │    │
│  │  ├── Deployment (replicas, resource limits)                         │    │
│  │  ├── Service (ClusterIP)                                            │    │
│  │  ├── HPA (autoscaling on CPU/request rate)                          │    │
│  │  └── Ingress (external access)                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                   │                                          │
│                                   ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Monitoring & Observability                        │    │
│  │                                                                     │    │
│  │  Operational (Prometheus + Grafana):                                │    │
│  │  ├── Request latency (p50, p95, p99)                               │    │
│  │  ├── Error rate (4xx, 5xx)                                         │    │
│  │  ├── Throughput (requests/sec)                                     │    │
│  │  ├── Pod health (restarts, OOMKills)                               │    │
│  │  └── Resource utilization (CPU, memory)                            │    │
│  │                                                                     │    │
│  │  ML-Specific (Evidently):                                          │    │
│  │  ├── Data drift score                                              │    │
│  │  ├── Prediction distribution shift                                 │    │
│  │  ├── Feature quality (nulls, out-of-range)                         │    │
│  │  └── Model accuracy (when ground truth available)                  │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                        │
│                              Alert fires                                     │
│                                     │                                        │
│                                     ▼                                        │
│                        ┌─────────────────────┐                              │
│                        │  Alerting + SLOs     │                              │
│                        │  ├── Latency SLO     │                              │
│                        │  ├── Availability    │                              │
│                        │  ├── Drift threshold │                              │
│                        │  └── Quality gate    │                              │
│                        └──────────┬───────────┘                              │
│                                   │                                          │
│                          ┌────────┴────────┐                                │
│                          ▼                  ▼                                │
│              ┌──────────────────┐  ┌──────────────────┐                     │
│              │ Page on-call     │  │ Trigger retrain  │                     │
│              │ (incident)       │  │ (automated)      │                     │
│              └──────────────────┘  └──────────────────┘                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. Data Source

**What:** [Describe your data source — dataset name, format, how it's ingested]

**Technology:** [e.g., CSV file, PostgreSQL, API endpoint]

**Notes:** [Any data-specific considerations — PII, size, refresh frequency]

---

### 2. Training Pipeline

**What:** Automated pipeline that validates data, trains a model, evaluates quality, and registers the artifact.

**Technology:** Prefect (Python-native orchestrator)

**Key decisions:**
- [Why Prefect over alternatives?]
- [What's the evaluation gate threshold and why?]
- [How is the pipeline triggered? (schedule, drift alert, manual)]

---

### 3. Model Registry

**What:** Versioned storage for trained models with stage promotion (None → Staging → Production).

**Technology:** MLflow Model Registry

**Key decisions:**
- [Promotion criteria — what must pass before a model moves to Production?]
- [Retention policy — how many versions do you keep?]
- [Rollback strategy — how do you revert to a prior version?]

---

### 4. Model Serving

**What:** REST API serving predictions from the production model.

**Technology:** FastAPI + Docker + Kubernetes

**Endpoints:**
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Liveness/readiness probe |
| `/predict` | POST | Model inference |
| `/metrics` | GET | Prometheus metrics scrape |

**Key decisions:**
- [Why FastAPI over Flask/BentoML/KServe?]
- [Container base image and size considerations]
- [Resource limits (CPU/memory) — how did you size them?]

---

### 5. Kubernetes Deployment

**What:** Production-grade deployment with scaling, health checks, and resource governance.

**Technology:** Kubernetes (kind/minikube for local, adaptable to EKS/GKE)

**Resources:**
| Resource | Purpose |
|----------|---------|
| Deployment | Pod spec, replicas, rolling update |
| Service | Internal routing |
| HPA | Autoscaling policy |
| Namespace | Isolation |

**Key decisions:**
- [Replica count and scaling thresholds]
- [Rolling update strategy parameters]
- [Why plain k8s Deployment over KServe/Seldon?]

---

### 6. Monitoring Stack

**What:** Two-layer monitoring: operational metrics + ML-specific quality signals.

**Technology:** Prometheus + Grafana (operational), Evidently (ML-specific)

**Dashboards:**
| Dashboard | Metrics | Alert threshold |
|-----------|---------|-----------------|
| Operational | Latency, errors, throughput | [your thresholds] |
| Model Quality | Drift score, prediction distribution | [your thresholds] |
| Data Quality | Null rates, schema violations | [your thresholds] |

**Key decisions:**
- [Why these alert thresholds? How did you calibrate?]
- [Scrape interval — why that frequency?]
- [Dashboard design — what's the on-call "glance" view?]

---

### 7. SLOs & Alerting

**What:** Formal service level objectives defining acceptable performance.

**SLO Definitions:**

| SLO | Target | Window | Rationale |
|-----|--------|--------|-----------|
| Availability | [e.g., 99.5%] | [e.g., 30-day rolling] | [why this number] |
| Latency (p95) | [e.g., < 200ms] | [e.g., 5-min window] | [why this number] |
| Drift score | [e.g., < 0.3] | [e.g., per batch] | [why this threshold] |
| Data quality | [e.g., > 99% valid] | [e.g., per pipeline run] | [why this threshold] |

**Alert routing:**
- [Who gets paged for operational alerts?]
- [Who gets notified for drift alerts?]
- [What's the escalation path?]

---

### 8. Retraining Loop

**What:** Automated or semi-automated model retraining triggered by monitoring signals.

**Triggers:**
| Trigger | Condition | Action |
|---------|-----------|--------|
| Scheduled | [e.g., weekly cron] | Run full pipeline |
| Drift-triggered | [e.g., drift score > 0.3] | Run pipeline + alert team |
| Manual | Engineer triggers | Run pipeline with custom params |

**Key decisions:**
- [Fully automatic vs human-in-the-loop?]
- [What validation must pass before new model replaces current?]
- [Rollback criteria — when do you revert?]

---

## Data Flow (End-to-End)

```
Raw Data
    │
    ▼
Schema Validation (fail → alert, stop)
    │
    ▼
Feature Engineering
    │
    ▼
Train/Test Split
    │
    ▼
Model Training (params logged to MLflow)
    │
    ▼
Evaluation Gate (fail → alert, stop; pass → continue)
    │
    ▼
Register in MLflow (version N)
    │
    ▼
Promote to Production (manual approval or automated)
    │
    ▼
Serve via FastAPI on Kubernetes
    │
    ▼
Predictions flow to users
    │
    ▼
Monitoring collects: latency, errors, predictions, input features
    │
    ▼
Evidently computes drift score against reference data
    │
    ├── Drift OK → continue serving
    │
    └── Drift detected → alert fires
                              │
                    ┌─────────┴─────────┐
                    ▼                     ▼
            Trigger retrain         Page on-call
            (automated)            (investigate)
                    │
                    ▼
            New model trained → evaluate → promote (loop restarts)
```

---

## Technology Choices & Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| ML Framework | scikit-learn | [Simple, sufficient for demo; focus is on ops, not model complexity] |
| Experiment Tracking | MLflow | [Industry standard, self-hosted, integrates with everything] |
| Serving Framework | FastAPI | [Fast, async, easy Prometheus integration, familiar to Python teams] |
| Container Runtime | Docker | [Standard, well-understood, good k8s integration] |
| Orchestrator | Kubernetes | [Your core strength; production-grade; matches real deployments] |
| Pipeline | Prefect | [Python-native, lightweight, great for ML workflows] |
| Operational Monitoring | Prometheus + Grafana | [Industry standard; you already know it] |
| ML Monitoring | Evidently | [Best open-source option for drift; generates actionable reports] |
| Alerting | Prometheus Alertmanager | [Integrates with Grafana; supports routing/silencing] |

---

## Failure Modes & Mitigation

| Failure Mode | Detection | Impact | Mitigation |
|-------------|-----------|--------|------------|
| Model serving pod crashes | k8s readiness probe fails | Predictions unavailable | Replicas + auto-restart; HPA maintains capacity |
| Model returns garbage predictions | Drift monitoring, prediction distribution shift | Users get bad results silently | Drift alert → retrain or rollback |
| Training pipeline fails | Prefect failure notification | Stale model stays in prod longer | Alert + manual investigation; current model continues serving |
| Data source becomes unavailable | Pipeline validation step fails | Can't retrain | Alert; current model continues serving; check data source |
| Gradual drift (concept drift) | Evidently drift score trends up | Slow accuracy degradation | Burn-rate alerting (not single-threshold) |
| Sudden data schema change | Validation step catches schema mismatch | Pipeline fails early | Alert team; investigate upstream data change |
| Resource exhaustion (OOM) | k8s OOMKill events in metrics | Pod restarts, brief unavailability | Resource limits + HPA + monitoring |
| MLflow registry unavailable | Health check on MLflow | Can't register new models; serving unaffected | MLflow HA setup; serving uses cached model |

---

## Operational Design Decisions

### Why these SLO thresholds?

[Fill in: Explain how you arrived at each number. What baseline did you measure? What's the user experience trade-off?]

### Why these alert thresholds?

[Fill in: Explain the difference between "something is degrading" and "something is broken." How did you avoid alert fatigue?]

### Why this retraining frequency?

[Fill in: Balance between freshness and compute cost. What cadence makes sense for your data?]

### Why human-in-the-loop (or fully automated)?

[Fill in: What's the risk of bad models reaching production? In banking, you probably want human approval. Explain that trade-off.]

---

## Sections to Complete After Implementation

- [ ] Fill in all [bracketed placeholders] with your actual decisions
- [ ] Update the architecture diagram to match your real components
- [ ] Add any additional components you integrated
- [ ] Document any deviations from the original plan and why
- [ ] Add performance baselines (actual latency numbers, actual drift thresholds)
- [ ] Include links to your Grafana dashboards (screenshots if running locally)
