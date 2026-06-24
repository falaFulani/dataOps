# Weeks 11–12 — Capstone: End-to-End MLOps System

**Time budget:** 12–16 hours total (split across two weeks)  
**Goal:** Integrate everything from Weeks 1–10 into a single, portfolio-worthy GitHub repository that demonstrates the full MLOps operational loop.  
**Key insight:** This isn't about building something new — it's about composing the pieces you already built into one coherent system, then documenting it well enough that an interviewer can see your thinking in 5 minutes.

---

## Project Overview

You're building a complete MLOps system in one repository. It should show:

1. A model goes from raw data to production serving
2. Monitoring catches when things degrade
3. Retraining triggers automatically
4. SLOs define "good" vs "not good"
5. Incident response is documented and rehearsed
6. Architecture decisions are explicit and justified

This is the project you link in your CV, walk through in interviews, and reference when someone asks: *"How do you think about ML in production?"*

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          MLOps Capstone System                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌───────────┐    ┌──────────────────────┐  │
│  │  Raw     │───▶│  Training    │───▶│  Model    │───▶│  Model Serving       │  │
│  │  Data    │    │  Pipeline    │    │  Registry │    │  (FastAPI + Docker)  │  │
│  │          │    │  (Prefect)   │    │  (MLflow) │    │  on Kubernetes       │  │
│  └──────────┘    └──────────────┘    └───────────┘    └──────────┬───────────┘  │
│       ▲                 ▲                                         │              │
│       │                 │                                         ▼              │
│       │                 │                              ┌──────────────────────┐  │
│       │                 │                              │  /predict endpoint   │  │
│       │                 │                              │  /health endpoint    │  │
│       │                 │                              └──────────┬───────────┘  │
│       │                 │                                         │              │
│       │          ┌──────┴───────┐                                │              │
│       │          │  Retraining  │◀─── Drift Alert ───┐           │              │
│       │          │  Trigger     │                    │           ▼              │
│       │          └──────────────┘              ┌─────┴──────────────────────┐   │
│       │                                        │  Monitoring Stack          │   │
│       │                                        │  ┌─────────────────────┐   │   │
│       │                                        │  │ Prometheus + Grafana│   │   │
│       │                                        │  │ (operational SLOs)  │   │   │
│       │                                        │  └─────────────────────┘   │   │
│       │                                        │  ┌─────────────────────┐   │   │
│       │                                        │  │ Evidently           │   │   │
│       │                                        │  │ (drift + quality)   │   │   │
│       │                                        │  └─────────────────────┘   │   │
│       │                                        └────────────────────────────┘   │
│       │                                                                          │
│       └──── New data / scheduled retrain ────────────────────────────────────────┘
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Supporting Artifacts:                                                            │
│  • SLO definitions + alerting rules                                              │
│  • Incident runbook + postmortem template                                        │
│  • Architecture Decision Records (ADRs)                                          │
│  • Demo script + Makefile for reproducibility                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Components to Integrate

| # | Component | Source Week | What you already have |
|---|-----------|-------------|----------------------|
| 1 | Trained, versioned model | Week 4 | MLflow experiment + registered model |
| 2 | Model API, containerized, on k8s | Weeks 5 + 7 | FastAPI service + Docker + k8s deployment |
| 3 | Retraining pipeline | Week 6 | Prefect flow: validate → train → evaluate → register |
| 4 | Monitoring: operational + drift | Week 8 | Prometheus/Grafana dashboards + Evidently reports |
| 5 | SLOs + alerting rules | Week 9 | SLO definitions + alert configs |
| 6 | Incident runbook + postmortem | Week 10 | ML incident runbook + postmortem template |
| 7 | Architecture decision record | NEW | ADR explaining why you chose each tool + threshold |

---

## Week 11 — Build & Integrate

**Focus:** Get the system working end-to-end in one repository.

### Tasks

- [ ] Create the repo structure (use this folder as your base)
- [ ] Copy/adapt your training pipeline from Week 6
- [ ] Copy/adapt your model serving code from Weeks 5 + 7
- [ ] Wire up MLflow tracking so training logs and registers automatically
- [ ] Deploy the model to your local k8s cluster (kind/minikube)
- [ ] Bring up the monitoring stack (Prometheus + Grafana + Evidently)
- [ ] Configure alerting rules for your SLOs
- [ ] Wire the retraining trigger: when drift alert fires → pipeline reruns
- [ ] Run through the full loop at least once: train → serve → generate predictions → see metrics → trigger retrain
- [ ] Write basic API tests (`make test` should pass)

### Suggested Repo Structure

```
mlops-capstone/
├── README.md                    # This file (project overview + architecture)
├── Makefile                     # Orchestrates everything
├── architecture.md             # Detailed architecture document
├── demo-script.md              # Interview demo walkthrough
├── interview-framing.md        # How to present this in interviews
│
├── adr/                         # Architecture Decision Records
│   └── 001-architecture-decisions.md
│
├── training/                    # Training pipeline
│   ├── pipeline.py             # Prefect flow
│   ├── pipeline_config.yml     # Training config
│   └── requirements.txt
│
├── serving/                     # Model serving
│   ├── app.py                  # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/                         # Kubernetes manifests
│   ├── deployment.yml
│   ├── service.yml
│   ├── hpa.yml
│   └── namespace.yml
│
├── monitoring/                  # Monitoring stack
│   ├── docker-compose.yml      # Prometheus + Grafana + Evidently
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── evidently/
│       └── drift_config.yml
│
├── runbook/                     # Operational docs
│   ├── incident-runbook.md
│   └── postmortem-template.md
│
├── slos/                        # SLO definitions
│   └── slo-definitions.yml
│
└── tests/                       # API + integration tests
    ├── test_api.py
    └── test_pipeline.py
```

---

## Week 12 — Document & Demo

**Focus:** Make it presentable. Documentation is what separates "I built a thing" from "I can communicate complex systems."

### Tasks

- [ ] Write the architecture document (see `architecture.md` template)
- [ ] Fill in your ADR with actual decisions you made
- [ ] Finalize the incident runbook (adapted from Week 10)
- [ ] Write SLO definitions with rationale for each threshold
- [ ] Create the architecture diagram (update the ASCII art above with your actual components)
- [ ] Write a clear README that a stranger could follow
- [ ] Practice the demo walkthrough (see `demo-script.md`)
- [ ] Record a 5-minute demo (optional, but high impact for interviews)
- [ ] Push to GitHub with a clean commit history
- [ ] Review: would a hiring manager at CloudFactory understand this in 2 minutes?

---

## How to Frame This in Interviews

**The one-liner:**  
> "I built an end-to-end MLOps system to ground my reliability and governance experience in ML — versioning, serving, monitoring, SLOs, and incident response."

**Why it works:**
- Shows you didn't just learn theory — you built the thing
- Demonstrates the operational mindset that's rare in ML engineers
- Connects your existing SRE/platform engineering strength to the ML domain
- The monitoring + SLOs + runbook combo is exactly what an ML support lead owns

**What it proves:**
- You can take a model from experiment to production
- You think about reliability from day one, not as an afterthought
- You understand ML-specific failure modes (drift, training-serving skew)
- You can document systems clearly (leadership signal)
- You can automate operational workflows (pipeline, alerting, retraining)

---

## Checklist

### Week 11
- [ ] Repository structure created
- [ ] Training pipeline runs end-to-end (data → model in registry)
- [ ] Model serving works locally (health check + predictions)
- [ ] Model deployed to local k8s
- [ ] Monitoring stack running (Prometheus + Grafana + Evidently)
- [ ] At least one alert rule configured and tested
- [ ] Retraining trigger wired (drift → retrain)
- [ ] Full loop demonstrated at least once
- [ ] `make test` passes

### Week 12
- [ ] Architecture document completed
- [ ] ADR filled with real decisions
- [ ] Incident runbook finalized
- [ ] SLO definitions documented with rationale
- [ ] README is clear and self-contained
- [ ] Demo walkthrough practiced (5-min and 15-min versions)
- [ ] Pushed to GitHub
- [ ] Could explain any component in 60 seconds if asked

### Portfolio Readiness
- [ ] A stranger can clone the repo and run `make demo`
- [ ] The README answers "what is this?" in 10 seconds
- [ ] Architecture diagram shows the full loop visually
- [ ] At least 3 ADRs explain non-obvious decisions
- [ ] The project links are in your CV/LinkedIn

---

## Remember

This capstone is portfolio evidence. It demonstrates the full operational loop — versioning, serving, monitoring, SLOs, incident response — grounded in ML-specific tooling.

Frame it as: *"I built this to ground my reliability and governance experience in ML."*

That's the story. The repo is the proof.
