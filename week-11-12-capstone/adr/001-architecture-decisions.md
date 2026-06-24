# Architecture Decision Records (ADRs)

ADRs document the *why* behind your technical choices. They're valuable because:
- They help future-you (or teammates) understand trade-offs you already evaluated
- They demonstrate systems thinking in interviews
- They show leadership: you don't just build, you make decisions explicit

**Format:** Each ADR follows: Context → Decision → Consequences

Fill in the sections below with your actual decisions as you build the capstone.

---

## ADR-001: Pipeline Orchestrator — Prefect over Airflow

### Status
Accepted

### Context

The system needs a pipeline orchestrator to automate: data validation → model training → evaluation → model registration. This pipeline runs on a schedule and can be triggered by drift alerts.

Options considered:
- **Apache Airflow** — industry standard, massive community, battle-tested
- **Prefect** — Python-native, modern, lightweight, hybrid execution model
- **Kubeflow Pipelines** — Kubernetes-native, Google-backed, scales massively
- **Argo Workflows** — k8s-native, container-first, GitOps-friendly
- **ZenML** — ML-specific abstractions, stack-agnostic

### Decision

Use **Prefect** for pipeline orchestration.

### Consequences

**Positive:**
- Pure Python — tasks are decorated functions, minimal boilerplate
- Local-first development — run and debug on laptop, deploy to prod later
- Built-in observability dashboard
- Lower operational overhead than Airflow (no scheduler/webserver/worker components)
- Fast iteration — change a task, re-run immediately

**Negative:**
- Smaller community than Airflow — fewer Stack Overflow answers
- Less battle-tested in enterprise environments
- Team may need to learn Prefect if they already know Airflow
- Self-hosted Prefect server adds a component (or pay for Prefect Cloud)

**Trade-off rationale:**
For a capstone/portfolio project demonstrating MLOps concepts, Prefect's simplicity means less time fighting infrastructure and more time showing the pipeline logic. For a production banking environment, Airflow's maturity might win — but the *concepts* are identical. An ADR like this documents that you evaluated the trade-off consciously.

---

## ADR-002: Serving Infrastructure — Plain Kubernetes over KServe/Seldon

### Status
Accepted

### Context

The trained model needs to be served as a REST API in production. Options for serving on Kubernetes:

- **Plain k8s Deployment + FastAPI** — standard container deployment, model loaded at startup
- **KServe (formerly KFServing)** — k8s-native model serving with autoscaling, canary, explainability
- **Seldon Core** — enterprise ML serving with A/B testing, drift detection built-in
- **BentoML** — Python-first model serving framework with built-in containerization

### Decision

Use **plain Kubernetes Deployment with FastAPI** for model serving.

### Consequences

**Positive:**
- Full control over the serving logic (custom preprocessing, metrics, health checks)
- No additional CRDs or operators to install and maintain
- Simpler debugging — it's just a container running a Python app
- Familiar patterns for any platform engineer
- Demonstrates understanding of the fundamentals, not just framework usage

**Negative:**
- No built-in canary deployments (would need to implement with Istio or Flagger)
- No built-in multi-model serving (one deployment per model)
- No built-in model explainability
- Manual implementation of A/B testing if needed later

**Trade-off rationale:**
For a single-model system focused on demonstrating operational excellence, the overhead of KServe/Seldon isn't justified. The complexity they add (CRDs, InferenceService resources, operator maintenance) exceeds the benefit for this scope. If scaling to 10+ models or needing canary rollouts, revisit this decision.

---

## ADR-003: SLO Thresholds — Availability and Latency Targets

### Status
[Accepted / Proposed — update after implementation]

### Context

The model service needs SLO definitions. These drive alerting, error budgets, and on-call response. The thresholds must balance:
- User experience (faster is better)
- Realistic operational targets (don't set 99.99% if infra can't support it)
- Alert fatigue (too sensitive = noise; too lax = miss real issues)

### Decision

| SLO | Target | Window | Burn-rate alert |
|-----|--------|--------|-----------------|
| Availability | 99.5% | 30-day rolling | Alert if 6h burn-rate projects budget exhaustion |
| Latency (p95) | < 200ms | 5-min window | Alert if sustained > 200ms for 10 minutes |
| Drift score | < 0.3 (Evidently dataset drift) | Per monitoring batch | Alert on single breach |
| Data quality | > 99% valid inputs | Per pipeline run | Alert on single breach |

### Consequences

**Positive:**
- 99.5% availability allows ~3.6 hours downtime/month — realistic for a non-critical internal service
- 200ms p95 latency is generous for a simple model; leaves room for model complexity growth
- Drift threshold of 0.3 is conservative — catches drift before it materially affects predictions
- Burn-rate alerting (not raw threshold) reduces noise from transient spikes

**Negative:**
- 99.5% may be too lax for a customer-facing service in banking (might need 99.9%)
- Drift threshold is heuristic — may need tuning after observing real baseline
- No ground-truth-based SLO (accuracy) since ground truth is often delayed

**Trade-off rationale:**
Start conservative (lower targets, wider windows), then tighten based on observed baselines. It's easier to tighten SLOs than to relax them — stakeholders resist loosening targets. The drift threshold of 0.3 is a starting point; calibrate against your model's actual baseline drift (some datasets naturally drift more).

[Fill in your actual thresholds after running the system and observing baselines]

---

## ADR-004: Monitoring Strategy — Two-Layer Approach

### Status
Accepted

### Context

ML systems can fail in ways that traditional monitoring misses. A model can return HTTP 200 with valid JSON while producing entirely wrong predictions. Need to decide:
- What to monitor
- Which tools for each layer
- How to unify alerting

### Decision

Implement **two-layer monitoring**:

1. **Operational layer (Prometheus + Grafana):**
   - Request latency (histogram)
   - Error rate (counter)
   - Throughput (counter)
   - Pod health (k8s metrics)
   - Resource utilization

2. **ML quality layer (Evidently):**
   - Data drift (feature distribution shift)
   - Prediction drift (output distribution shift)
   - Data quality (null rates, out-of-range values)
   - Model performance (when ground truth available)

Both layers feed into **Prometheus Alertmanager** for unified alerting.

### Consequences

**Positive:**
- Catches both infrastructure failures (ops layer) and silent model degradation (ML layer)
- Uses industry-standard tools — transferable skills
- Unified alerting path — one place to manage routing and silencing
- Evidently reports are human-readable — useful for sharing with data science team

**Negative:**
- Two systems to maintain (Prometheus stack + Evidently)
- Evidently runs batch analysis, not real-time — there's a detection lag
- Need to bridge Evidently outputs into Prometheus metrics (custom exporter)
- More complex than single-tool solutions (e.g., Arize does both, but costs money)

**Trade-off rationale:**
Real-time drift detection (e.g., streaming analysis on every request) adds complexity and cost that isn't justified for most use cases. Batch analysis every N minutes or every N requests is sufficient — you're detecting trends, not individual bad predictions. The lag is acceptable because drift is a gradual phenomenon.

---

## ADR-005: Retraining Strategy — Semi-Automated with Human Gate

### Status
[Accepted / Proposed — update after implementation]

### Context

When monitoring detects drift, the system can:
1. Fully automated: retrain → evaluate → promote automatically
2. Semi-automated: retrain → evaluate → wait for human approval → promote
3. Manual: alert human → human decides whether to retrain

In a banking context, models affect financial decisions. Bad models have regulatory and financial consequences.

### Decision

Use **semi-automated retraining with a human approval gate** for production promotion.

- Retraining triggers automatically (drift alert or schedule)
- Evaluation runs automatically (quality gate)
- Promotion to production requires human approval (Slack notification + explicit action)
- Rollback is automated (if new model performs worse, revert immediately)

### Consequences

**Positive:**
- Reduces time-to-fix for drift (retrain starts immediately, no human needed to initiate)
- Human gate prevents untested models from reaching production
- Rollback automation limits blast radius of a bad model
- Audit trail: who approved, when, based on what metrics
- Regulatory alignment: human-in-the-loop for consequential decisions

**Negative:**
- Adds latency to the promotion process (waiting for human)
- Requires someone to be available to approve (on-call consideration)
- Semi-automated is more complex than fully automated or fully manual
- Risk of approval becoming rubber-stamp if too frequent

**Trade-off rationale:**
In banking, the cost of a bad model in production (regulatory risk, financial loss, customer impact) outweighs the cost of delayed promotion (serving a slightly stale model for a few hours). Fully automated is appropriate for low-risk models (e.g., content recommendation). For financial models, human approval is non-negotiable until trust is established.

---

## Template for Additional ADRs

Copy this template for new decisions:

```markdown
## ADR-XXX: [Decision Title]

### Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

### Context

[What is the problem? What forces are at play? What constraints exist?]

### Decision

[What did you decide? Be specific.]

### Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Drawback 1]
- [Drawback 2]

**Trade-off rationale:**
[Why is this the right trade-off for your context?]
```

---

## ADRs to Consider Adding

As you build the capstone, consider documenting decisions about:

- [ ] Dataset choice — why this dataset for the demo?
- [ ] Model complexity — why a simple model vs a complex one?
- [ ] Container base image — why this image? Security considerations?
- [ ] Namespace strategy — why a single namespace vs multi-namespace?
- [ ] Secret management — how are model artifacts and configs secured?
- [ ] CI/CD integration — if you add GitHub Actions, why that trigger strategy?
- [ ] Feature store — do you need one? Why or why not?
- [ ] Model versioning vs model lineage — what's tracked and why?
