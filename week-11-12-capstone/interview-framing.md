# Interview Framing — How to Present the Capstone

This document helps you articulate the capstone project in interviews.
It's not about memorizing scripts — it's about having clear anchors for each talking point so you can speak naturally.

---

## The One-Liner Pitch

> "I built an end-to-end MLOps system — from training through production serving with monitoring, SLOs, and automated retraining — to ground my 8 years of reliability engineering in ML-specific tooling."

Use this when someone asks "tell me about a recent project" or "what have you been working on?"

---

## The 2-Minute System Walkthrough

Use this when someone says "walk me through it" or "how does it work?"

**Paragraph 1 — What it does (30 sec):**

> "It's a complete MLOps system in one repository. A model gets trained through an automated pipeline, registered with version control, served as an API on Kubernetes, and monitored for both operational health and model-specific drift. When drift is detected, it triggers retraining. The full loop is automated, but model promotion to production has a human approval gate — which is the right pattern for regulated environments like banking."

**Paragraph 2 — How it's built (30 sec):**

> "The stack is: Prefect for pipeline orchestration, MLflow for experiment tracking and model registry, FastAPI for serving, Docker and Kubernetes for deployment, Prometheus and Grafana for operational monitoring, and Evidently for drift detection. Everything's connected — metrics feed into SLO definitions, SLO violations trigger alerts, alerts trigger either retraining or incident response depending on the failure mode."

**Paragraph 3 — Why it matters (30 sec):**

> "I built this because ML systems fail differently from traditional services. A model can return 200 OK while its predictions have degraded — you won't catch that with standard monitoring. The two-layer approach — operational metrics plus ML-quality metrics — catches both classes of failure. That's the gap most teams have, and it's where my reliability engineering background applies directly."

**Paragraph 4 — What it demonstrates (30 sec):**

> "The project demonstrates that I can design the full operational lifecycle for ML systems: not just deployment, but monitoring, SLOs, incident response, and governance. The documentation — architecture decisions, runbooks, postmortem templates — shows how I'd onboard a team and establish operational standards. It's the bridge between platform engineering and MLOps."

---

## Questions This Capstone Answers About You

| Question in the interviewer's mind | How the capstone answers it |
|---|---|
| "Can he actually do MLOps, or just talk about it?" | Working system with code, deployments, monitoring |
| "Does he understand ML-specific failure modes?" | Drift monitoring, two-layer observability, ML incident runbook |
| "Can he design systems, not just implement them?" | Architecture doc, ADRs, SLO rationale |
| "Is he a leader or just an individual contributor?" | Documentation, runbooks, team-enabling artifacts |
| "Can he work in regulated environments?" | Human approval gates, audit trails, governance patterns |
| "Does he understand the full lifecycle?" | Training → serving → monitoring → retraining loop |
| "Can he communicate complex systems?" | Clear README, demo walkthrough, architecture diagram |
| "Will he improve our operational maturity?" | SLO definitions, alerting frameworks, postmortem culture |

---

## How It Demonstrates Leadership + Technical Depth

### Technical Depth Signals

- **Systems design:** The architecture shows you think in components, data flows, and failure modes — not just features.
- **Production mindset:** SLOs, alerting, incident response, and rollback strategies are baked in from the start, not bolted on.
- **Tool fluency:** You chose tools deliberately (documented in ADRs) and can explain trade-offs.
- **Operational excellence:** Monitoring, observability, and governance are first-class concerns, not afterthoughts.

### Leadership Signals

- **Documentation:** You write for others, not just for yourself. The README, architecture doc, and runbooks enable a team.
- **Decision transparency:** ADRs show you make decisions explicitly and invite challenge.
- **Process design:** Runbooks and postmortem templates show you build repeatable processes, not just one-off solutions.
- **Strategic thinking:** You connect technology choices to business context (regulated environment, risk tolerance, team skill mix).

---

## CloudFactory-Specific Connections

The CloudFactory ML Support Lead role (based on the job description) needs someone who can:

| Job Requirement | How the capstone demonstrates it |
|---|---|
| "Harden and extend alerting frameworks" | Two-layer monitoring + SLO burn-rate alerting + Evidently drift detection |
| "Incident governance and response" | ML incident runbook + postmortem template + escalation paths |
| "Support ML systems in production" | Full production deployment with health checks, scaling, monitoring |
| "Lead a technical team" | Documentation-first approach, ADRs, clear system boundaries for team ownership |
| "Bridge platform and ML engineering" | The project IS this bridge — platform tools applied to ML workloads |
| "Kubernetes and container orchestration" | k8s deployment with HPA, resource limits, rolling updates |
| "Improve operational maturity" | SLOs, error budgets, observability, governance artifacts |

### How to Reference CloudFactory Directly

In the interview, you can say:

> "I noticed the role involves hardening alerting frameworks for ML systems. I built exactly that in this project — the two-layer monitoring approach catches both infrastructure failures and silent model degradation. The SLO burn-rate alerting is specifically designed to reduce noise while catching real degradation early."

> "The incident governance piece maps directly to my experience running postmortems and building runbooks in banking. I extended that to cover ML-specific incidents — drift events, data quality failures, retraining decisions — because those incidents don't fit traditional on-call playbooks."

> "I see the role as bridging platform engineering and ML. This project is my proof that the bridge works — the operational patterns transfer, you just need ML-specific instrumentation on top."

---

## Common Follow-Up Questions & Answers

### "What was the hardest part?"

> "Calibrating drift thresholds. Unlike latency or error rate where there are industry norms, drift thresholds are dataset-specific. I had to run the baseline, observe natural variation, then set thresholds that catch real degradation without firing on normal variance. It's the ML equivalent of tuning alert sensitivity — same skill, different domain."

### "What would you add next?"

> "Three things: (1) A/B testing infrastructure to compare model versions in production with real traffic. (2) A feature store to standardize feature computation between training and serving — that eliminates training-serving skew. (3) Model explainability (SHAP values) exposed via the API so business users can understand predictions."

### "How would this scale to production?"

> "The k8s layer scales horizontally already — HPA handles traffic spikes. For multi-model serving, I'd add a model router and per-model SLOs. For the monitoring stack, Prometheus federates well and Grafana supports multi-tenant dashboards. The pipeline orchestrator (Prefect) supports concurrent flows. The architecture is designed to scale each component independently."

### "Why not use [some other tool]?"

> "I documented my tool choices as ADRs — each one has context, the decision, and the trade-offs. The short answer is usually: I optimized for simplicity and learning velocity in this project, with a clear path to production-grade alternatives. For example, Prefect over Airflow — same concepts, lighter setup, and the orchestration patterns are transferable."

### "How does this relate to your banking experience?"

> "In banking, I run production systems where failures have regulatory and financial consequences. MLOps adds a new failure mode — silent model degradation — that traditional monitoring misses. My contribution is bringing the same governance rigor (SLOs, incident response, audit trails) to this new failure class. The regulatory context means I naturally think about approval gates, lineage, and explainability."

### "Can you show me the monitoring dashboard?"

> "Yes — [show Grafana]. Top row is operational: latency percentiles, error rate, throughput. This tells me if the service is healthy. Bottom row is ML-specific: drift score over time, prediction distribution, data quality metrics. This tells me if the model is still making good predictions. The key insight is: the service can be healthy (top row green) while the model is degraded (bottom row red). That's the failure mode this setup catches."

---

## Interview Format Adaptations

### If it's a 30-min screen
- Use the one-liner + 2-minute walkthrough
- Be ready to deep-dive on one component if asked
- Have the GitHub repo URL ready to share

### If it's a 60-min technical interview
- Walk through the 15-min demo version
- Expect to be asked to go deeper on k8s, monitoring, or pipeline design
- Be ready to whiteboard variations or extensions

### If it's a system design interview
- Use the architecture diagram as your starting framework
- Extend it: "What if we need to serve 10 models?" "What if traffic 10x?"
- Show you think about scaling, failure modes, and operational cost

### If it's a leadership/behavioral interview
- Emphasize: ADRs, documentation, runbooks, team enablement
- Frame it as: "I build systems that teams can own, not just systems that work"
- Connect to: incident governance, postmortem culture, operational standards

---

## The Closing Statement

Use at the end of any interview segment about this project:

> "This project is portfolio evidence that my reliability and governance experience extends to ML systems. I built the full operational loop — not just the happy path — because I've spent 8 years learning that production is where the interesting problems live."
