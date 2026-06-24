# Demo Script — MLOps Capstone Walkthrough

Use this script to record a demo video or walk through the system in an interview.
Two versions: 5-minute highlights, 15-minute full walkthrough.

---

## Before the Demo

### Setup Checklist

- [ ] All services running (`make status` shows all green)
- [ ] Grafana dashboard loaded and showing data
- [ ] MLflow UI accessible with at least 2 experiment runs
- [ ] Terminal ready with the repo open
- [ ] Browser tabs pre-opened: Grafana, MLflow, API docs

### Opening Line

> "I built an end-to-end MLOps system that takes a model from training to production, with monitoring, SLOs, and automated retraining. Let me show you how it works."

---

## 5-Minute Version (Quick Highlights)

Use this for: initial interviews, quick portfolio walkthrough, video recording.

### Minute 0–1: The Architecture (show README)

**Show:** The architecture diagram in the README.

**Say:**
> "This system has five main pieces: a training pipeline that versions models in MLflow, an API serving layer running on Kubernetes, operational monitoring with Prometheus and Grafana, ML-specific monitoring with Evidently for drift detection, and a retraining loop that triggers when drift is detected."

**Talking point:** Emphasize the *loop* — this isn't a one-shot deployment, it's a living system.

---

### Minute 1–2: Training Pipeline (run or show output)

**Show:** Run `make train` or show a previous run's output.

**Say:**
> "The training pipeline validates the data schema, trains the model, evaluates against a quality gate, and only registers in MLflow if metrics pass. If data quality fails or accuracy is below threshold, the pipeline stops and alerts. This is CI for models."

**Talking point:** Quality gates prevent bad models from reaching production — same principle as deploy gates.

---

### Minute 2–3: Serving + Kubernetes (show the deployment)

**Show:** `kubectl get pods -n mlops-capstone`, then hit the `/health` and `/predict` endpoints.

**Say:**
> "The model is wrapped in a FastAPI service, containerized, and deployed on Kubernetes with health probes, resource limits, and an HPA for autoscaling. It's a standard k8s deployment — just the payload is a model instead of business logic."

**Talking point:** This is where your platform engineering background makes you immediately effective.

---

### Minute 3–4: Monitoring + SLOs (show Grafana)

**Show:** The Grafana dashboard with both operational and drift panels.

**Say:**
> "I monitor two layers. Operational: latency p95, error rate, throughput — standard SRE metrics. ML-specific: data drift scores, prediction distribution shifts. Both layers feed into SLOs. If the latency SLO burns too fast or drift crosses threshold, alerts fire."

**Talking point:** Most ML teams only monitor operational health. Adding the drift layer is what makes this MLOps, not just DevOps-for-ML.

---

### Minute 4–5: The Loop + Incident Response (show the connection)

**Show:** Alert rule in Prometheus → points to the retrain trigger → show the runbook.

**Say:**
> "When drift is detected, two things happen: the retraining pipeline triggers to produce a fresh model, and the on-call gets an alert with a runbook. The runbook covers triage: is this data drift or concept drift? Should we retrain, rollback, or investigate upstream? This is the operational governance layer that's often missing in ML systems."

**Talking point:** This is where your incident management and governance experience becomes a differentiator.

---

### Closing (5-sec)

> "The full system is in one repo with a Makefile, architecture docs, ADRs, and SLO definitions. I built it to ground my reliability engineering experience in ML-specific tooling."

---

## 15-Minute Version (Full Walkthrough)

Use this for: technical deep-dives, final-round interviews, team presentations.

### Minutes 0–2: Context & Architecture

**Show:** README → architecture diagram → repo structure

**Say:**
> "Let me set the context. I'm a platform/DevOps engineer with 8 years of experience running production systems in banking — Kubernetes, SLOs, incident governance, the full stack. I built this project to extend that operational depth into the ML domain."

**Walk through the architecture diagram:**
- Point to each component
- Explain the data flow direction
- Highlight the feedback loop (monitoring → retrain → serve → monitor)

**Talking points:**
- Why the loop matters: ML systems degrade silently without it
- Why operational + ML monitoring: they catch different failure modes
- Why architecture docs: leadership signal — you can communicate systems, not just build them

---

### Minutes 2–5: Training Pipeline Deep Dive

**Show:** `training/pipeline.py` → `pipeline_config.yml` → MLflow UI

**Demo:**
1. Show the pipeline code — point out the Prefect decorators, the validation step, the quality gate
2. Run `make train` live (or show recent output)
3. Open MLflow UI — show the experiment, logged parameters, metrics, artifact
4. Show model versions and stages (Staging → Production promotion)

**Say:**
> "The pipeline is orchestrated with Prefect. Four steps: validate data schema, train, evaluate against a threshold, register if it passes. All parameters are logged to MLflow so every run is reproducible and auditable. The config is externalized — changing hyperparameters doesn't require code changes."

**Talking points:**
- Reproducibility is a compliance requirement in banking
- Quality gates prevent regressions — same pattern as deploy gates
- MLflow gives you versioning and rollback — like artifact versioning for containers
- Config/code separation is a governance pattern you already enforce

---

### Minutes 5–8: Serving & Deployment

**Show:** `serving/app.py` → `Dockerfile` → `k8s/` manifests → live pods

**Demo:**
1. Show the FastAPI app — endpoints, Prometheus instrumentation
2. Show the Dockerfile — multi-stage build, security considerations
3. Show k8s manifests — deployment, service, HPA
4. `kubectl get pods -n mlops-capstone` — show running pods
5. Hit `/health` and `/predict` — show live responses
6. Show the HPA config — explain scaling thresholds

**Say:**
> "Serving is a FastAPI app exposing three endpoints: health for k8s probes, predict for inference, and metrics for Prometheus scraping. It's containerized and deployed with standard k8s patterns — rolling updates, resource limits, HPA. This should feel familiar to anyone running services in production."

**Talking points:**
- Resource limits: sized based on actual load testing, not guesses
- HPA: scales on CPU or custom metrics (request rate)
- Rolling update strategy: zero-downtime deployments for model updates
- This is your wheelhouse — emphasize confidence here

---

### Minutes 8–11: Monitoring & SLOs

**Show:** Grafana dashboards → Prometheus alert rules → SLO definitions

**Demo:**
1. Open Grafana — show the operational dashboard (latency, errors, throughput)
2. Switch to the ML dashboard (drift score, prediction distribution)
3. Show alert rules in Prometheus — explain each threshold
4. Open `slos/slo-definitions.yml` — walk through each SLO

**Say:**
> "I monitor at two layers. Operational metrics — latency, error rate, throughput — tell me if the service is healthy. ML metrics — drift score, prediction distribution — tell me if the model is still making good predictions. Both feed into SLOs. The availability SLO is 99.5% over a 30-day window. The drift SLO alerts if the burn-rate suggests we'll exhaust our error budget within a week."

**Talking points:**
- Two-layer monitoring is the key insight — most teams only have one
- SLO burn-rate alerting avoids noise from single-point spikes
- Drift detection catches silent failures — the model returns 200 OK but predictions are wrong
- This is the "harden our alerting frameworks" requirement from the job description

---

### Minutes 11–13: Retraining Loop & Incident Response

**Show:** Alert configuration → retraining trigger → runbook → postmortem template

**Demo:**
1. Show how a drift alert triggers the retraining pipeline
2. Walk through the runbook: triage → diagnose → decide (retrain vs rollback vs investigate)
3. Show the decision tree: when to retrain vs when to rollback
4. Show the postmortem template — adapted for ML incidents

**Say:**
> "When drift is detected, the system can retrain automatically, but in a regulated environment like banking, you probably want human approval before promoting a new model. The runbook gives the on-call engineer a decision tree: is this data drift, concept drift, or an upstream data issue? Each has a different response. The postmortem template captures learnings and feeds back into SLO tuning."

**Talking points:**
- Automated retraining vs human-in-the-loop: trade-off depends on risk tolerance
- Banking context: you'd likely require human approval for model promotion
- The runbook bridges the gap between ML engineers and platform/SRE teams
- Postmortem culture: you already do this for incidents, now extend to ML

---

### Minutes 13–15: Architecture Decisions & Summary

**Show:** `adr/001-architecture-decisions.md` → overall repo structure

**Demo:**
1. Walk through 2–3 ADRs: why Prefect over Airflow, why these SLO thresholds, why plain k8s
2. Show the overall repo structure — emphasize documentation is first-class
3. Run `make status` to show everything's connected

**Say:**
> "Every major decision is documented as an ADR — Architecture Decision Record. Why Prefect over Airflow? Why these thresholds? Why plain Kubernetes deployments over KServe? These aren't just technical choices — they're trade-off analyses. I chose tools that balance simplicity with production-readiness, and documented why so a new team member can understand the system in an hour."

**Closing:**
> "This project demonstrates the full operational loop for ML systems: versioning, serving, monitoring, SLOs, incident response, and governance. I built it to ground my 8 years of reliability engineering experience in ML-specific tooling. The skills transfer — the mental models are the same, the tools are new."

---

## Key Talking Points (Reference Card)

Keep these in your back pocket for any question that comes up:

| Topic | Your angle |
|-------|-----------|
| **Why this project?** | "To ground my ops experience in ML tooling — prove the skills transfer" |
| **Hardest part?** | "Calibrating drift thresholds — there's no universal right answer, it's domain-specific" |
| **What would you add?** | "A/B testing infrastructure, model explainability (SHAP), and a proper feature store" |
| **How does this scale?** | "The k8s layer scales horizontally. For multi-model, you'd add a model router and per-model SLOs" |
| **Banking relevance?** | "Model governance, audit trails, and approval gates are non-negotiable in regulated environments" |
| **Team leadership?** | "The docs, ADRs, and runbooks are how I'd onboard a team. Clear systems enable autonomy." |
| **What surprised you?** | "How much ML monitoring differs from service monitoring — the model can be 'up' but wrong" |

---

## CloudFactory-Specific Framing

When presenting to CloudFactory specifically, emphasize:

1. **"Harden alerting frameworks"** — Show the two-layer monitoring + SLO burn-rate alerting. This is literally their job requirement.

2. **"ML incident governance"** — Show the runbook + postmortem template. This is the process they need someone to build and lead.

3. **"Bridge ML and platform"** — The architecture shows you understand both worlds. You're not just a platform engineer guessing at ML — you've built the ML monitoring layer.

4. **"Team enablement"** — The documentation (ADRs, runbooks, architecture doc) shows how you'd onboard and lead a team. You don't just build — you make systems understandable.

5. **"Production mindset from day one"** — The project isn't a notebook or a demo — it's a production-grade system with failure modes, SLOs, and incident response. That's the mindset they need.

---

## Recording Tips (if making a video)

- Use a clean terminal with large font (14pt+)
- Pre-run everything once so there are no cold-start delays
- Keep browser tabs pre-loaded
- Speak slightly slower than feels natural
- End each section with a one-sentence summary
- Total video: aim for under 7 minutes (edit the 15-min version down)
- Upload to YouTube (unlisted) and link in your CV
