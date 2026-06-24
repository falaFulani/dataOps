# Week 6 — ML Pipelines & Orchestration

**Time budget:** 8–10 hours  
**Goal:** Build an automated ML pipeline that validates data, trains, evaluates, and registers a model — then understand when and why to retrain on a schedule.  
**Key insight:** This is CI/CD for models. Same governance instincts as your deploy pipelines, just the steps are data-validate → train → evaluate → register instead of lint → build → test → deploy.

---

## Concepts to Cover

### 1. What an ML Pipeline Orchestrator Does

An ML pipeline orchestrator manages **DAGs (Directed Acyclic Graphs) of ML tasks** — just like your CI/CD system manages build/test/deploy stages.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Validate    │────▶│    Train     │────▶│   Evaluate   │────▶│   Register   │
│    Data      │     │    Model     │     │    Model     │     │    Model     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                      │
   Check schema        Log params          Gate on metrics       Save artifact
   Check nulls         Track run           Fail if below          Version it
   Check ranges        Cache results       threshold              Promote it
```

Each box is a **task** (or step). Arrows are **dependencies**. The orchestrator:
- Executes tasks in the right order
- Handles retries on transient failures
- Caches results to avoid re-running expensive steps
- Tracks lineage (which data + code → which model)
- Provides observability (logs, status, duration per step)

### 2. Why ML Needs Orchestration

In traditional software, you build once and deploy. In ML, you retrain repeatedly because:

- **Data changes** — new customer behaviors, market shifts, seasonal patterns
- **Model drift** — yesterday's accurate model degrades over time (Week 5's monitoring catches this)
- **Compliance** — regulators want reproducible, auditable training runs (critical in banking)
- **Scale** — you might retrain dozens of models weekly; manual runs don't scale

Without orchestration you get:
- Jupyter notebooks run manually by data scientists (no audit trail)
- "It works on my machine" training runs (not reproducible)
- Models promoted to prod without evaluation gates (no quality control)
- No retry logic on transient infra failures (wasted time)

**Bottom line:** An ML pipeline is production automation for model creation, just like your Jenkins/GitHub Actions pipelines are production automation for service deployment.

### 3. Scheduled Retraining — When & Why

| Trigger | When to use | Example |
|---------|------------|---------|
| **Time-based (cron)** | Stable data cadence, regulatory requirement | Retrain fraud model every Sunday at 02:00 |
| **Data-volume-based** | New data arrives in batches | Retrain after 10k new labeled transactions |
| **Drift-triggered** | Monitoring detects degradation | Retrain when accuracy drops below 0.85 |
| **On-demand** | Ad-hoc experiments, hotfixes | Data scientist pushes new features, triggers retrain |

In banking, **time-based + drift-triggered** is the most common pattern. You schedule a weekly retrain as baseline, but also trigger early if monitoring (Week 5) flags drift.

Think of it as: scheduled retraining = cron deployment with quality gates.

### 4. Pipeline Concepts

| Concept | What it means | CI/CD equivalent |
|---------|--------------|-----------------|
| **Task / Step** | A single unit of work (validate, train, evaluate) | A job in your pipeline |
| **Flow / Pipeline** | The full DAG of tasks | Your entire CI/CD pipeline |
| **Dependency** | Task B runs only after Task A succeeds | Job dependency / `needs:` |
| **Artifact** | Output of a task (model file, metrics report) | Build artifact |
| **Retry** | Re-run a failed task N times before giving up | Retry policy on a CI job |
| **Caching** | Skip re-running a task if inputs haven't changed | Build cache / layer cache |
| **Parameters** | Configurable inputs to a pipeline run | Pipeline variables / env vars |
| **Concurrency** | Run independent tasks in parallel | Parallel jobs |
| **Idempotency** | Running the same pipeline twice produces same result | Idempotent deployments |

### 5. Tools Landscape

| Tool | Strengths | Best for |
|------|----------|----------|
| **Prefect** | Python-native, lightweight, great DX, hybrid execution | Teams starting out, Python-heavy workflows |
| **ZenML** | ML-specific abstractions, stack-agnostic, integrates with MLflow | End-to-end MLOps with swappable infra |
| **Kubeflow Pipelines** | Kubernetes-native, scales massively, Google-backed | Orgs already deep in K8s (you'd be comfortable here) |
| **Apache Airflow** | Battle-tested, huge community, general-purpose | Data engineering + ML, complex scheduling |
| **Argo Workflows** | K8s-native, container-first, GitOps-friendly | K8s shops wanting workflow automation |

**We'll use Prefect** for this week because:
- Pure Python — no infra to set up, no YAML to wrestle
- Decorators turn any function into a pipeline task (minimal boilerplate)
- Local-first — run and debug on your laptop, deploy to prod later
- Great observability dashboard out of the box
- You already know K8s/Argo; Prefect shows you the Python-native approach

> Once you understand pipeline orchestration concepts with Prefect, moving to Kubeflow or Argo is just swapping the execution layer — the mental model is identical.

### 6. Mapping Table: ML Pipeline ↔ CI/CD Pipeline

| CI/CD Pipeline | ML Pipeline | Why it's the same instinct |
|----------------|-------------|---------------------------|
| `lint` | `validate_data` | Catch garbage before it propagates |
| `build` | `train_model` | Transform source (code/data) into artifact (binary/model) |
| `test` | `evaluate_model` | Gate on quality metrics before promotion |
| `deploy` | `register_model` | Promote artifact to a registry for serving |
| Pipeline failure → alert | Pipeline failure → alert | Same incident response |
| Scheduled deployment | Scheduled retraining | Same cron governance |
| Build cache | Training cache | Don't redo work if inputs unchanged |
| Pipeline variables | Pipeline config (YAML) | Separate config from code |
| Artifact versioning | Model versioning | Rollback capability |
| `--no-cache` rebuild | Force retrain | When you need a clean run |

---

## Hands-on Lab

### Run the Pipeline

```bash
# 1. Set up environment
chmod +x setup.sh
./setup.sh

# 2. Activate
source venv/bin/activate

# 3. Run the pipeline
python pipeline.py
```

The pipeline will:
1. Load and validate the Iris dataset (schema, nulls, ranges)
2. Train a RandomForest classifier with logged parameters
3. Evaluate against an accuracy threshold (quality gate)
4. Register/save the model only if evaluation passes

### Experiment

- Change `min_accuracy_threshold` in `pipeline_config.yml` to `0.99` — watch the pipeline fail at evaluation (same as a test gate failing your deploy)
- Change `n_estimators` to `1` — watch accuracy drop and potentially fail the gate
- Break the data validation by adding invalid ranges — watch the pipeline fail early

### Inspect the Config

Open `pipeline_config.yml` — this is your pipeline's "values file" (like Helm values or GitHub Actions variables). Config lives separately from logic.

---

## Key Takeaways for Your Role

1. **Governance:** Every model reaching production went through an auditable, repeatable pipeline — not a notebook someone ran at 2 AM.
2. **Quality gates:** Same as your deploy pipelines — if metrics don't pass, the model doesn't ship.
3. **Scheduling:** Models need periodic retraining. You'll manage the schedule and failure alerting just like cron jobs.
4. **Reproducibility:** Pipeline + config + data version = you can recreate any model. Essential for regulators.
5. **Failure modes:** Pipeline failures are your incidents. Same response patterns — alert, diagnose, fix, retro.

---

## Resources

- 📚 [Prefect Docs — Tutorials](https://docs.prefect.io/latest/tutorial/) — start with "Flows" and "Tasks"
- 📚 [ML Pipelines: Concepts (Google Cloud)](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- 📚 [Kubeflow Pipelines Overview](https://www.kubeflow.org/docs/components/pipelines/overview/) — for when you're ready to go K8s-native
- 📚 [ZenML — Why Pipelines?](https://docs.zenml.io/user-guide/starter-guide/create-an-ml-pipeline)
- 📚 [Argo Workflows](https://argoproj.github.io/argo-workflows/) — K8s-native, you'll feel at home
- 📚 [Chip Huyen — Designing ML Systems, Ch. 10](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) — excellent pipeline architecture patterns

---

## Checklist

- [ ] Read through concepts above
- [ ] Run `setup.sh` and execute `pipeline.py` successfully
- [ ] Observe pipeline output — identify each stage and its logs
- [ ] Modify `pipeline_config.yml` to make the pipeline fail (raise threshold)
- [ ] Modify config to make it pass again (tune params or lower threshold)
- [ ] Explain to yourself: "How is this different from running a notebook manually?"
- [ ] Write 3–5 sentences comparing this to your CI/CD pipelines at work
- [ ] Sketch how you'd schedule this pipeline for weekly retraining (cron + alerting)
