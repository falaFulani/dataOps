# Week 4: Experiment Tracking & Model Registry

> **The Operator's Take:** You already version Docker images. You tag releases. You know that if you can't roll back to the last known good image, you're flying blind during an incident. Models are no different — except most ML teams learn this the hard way.

---

## Why Model Versioning Matters

You can't roll back what you didn't version.

Think about what happens when a service deployment goes bad at 2 AM:
1. You check which image tag is running in production
2. You roll back to the previous tag
3. Traffic restores, customers are happy, you go back to sleep

Now imagine the same scenario but for a fraud detection model:
- The new model is flagging 40% of legitimate transactions
- Nobody tagged the previous model
- Nobody recorded which training data or hyperparameters produced the last good version
- You're stuck retraining from scratch while the business bleeds money

**Model versioning gives you the same safety net you already have for services.** Every model artifact gets a version, every version gets metadata about how it was produced, and every promotion to production is an auditable event.

---

## What is a Model Registry?

A model registry is three things combined:

| Component | What it does | Ops equivalent |
|-----------|-------------|----------------|
| **Artifact store** | Stores the actual model files (serialized weights, pickled objects) | Container registry storing image layers |
| **Metadata catalog** | Tracks who trained it, when, with what data, what metrics it achieved | Image labels + build pipeline metadata |
| **Lifecycle manager** | Controls which version is in staging, production, or archived | Deploy environment promotion (dev → staging → prod) |

### Why not just use S3/GCS with naming conventions?

You *could*, the same way you *could* manage deployments with bash scripts and rsync. A registry gives you:
- Atomic transitions between stages
- Audit trail of who promoted what and when
- API access for CI/CD pipelines to pull the right model version
- Lineage tracking (which experiment produced this model?)

---

## Experiment Tracking

Every model training run is an experiment. Experiment tracking means logging:

- **Parameters** — hyperparameters, feature selections, data splits (your build args)
- **Metrics** — accuracy, F1 score, AUC, latency (your SLIs)
- **Artifacts** — the trained model file, plots, feature importance charts (your build outputs)
- **Environment** — Python version, library versions, hardware used (your Dockerfile)
- **Code version** — git commit hash (your image tag source)

### Why This Matters for Reproducibility

Imagine an SRE telling you "the service works on my machine" without being able to tell you which commit, which config, which environment variables. That's what ML without experiment tracking looks like.

**Full reproducibility requires:**
```
Code version (git SHA) + Data version (hash/snapshot) + Hyperparameters + Environment (deps) = Reproducible model
```

If any one of these is missing, you cannot reliably recreate a model — even on the same hardware.

---

## MLflow Concepts

MLflow is the open-source tool we'll use. Think of it as your model's CI/CD platform.

### Core Concepts

| MLflow concept | What it is | Ops analogy |
|----------------|-----------|-------------|
| **Experiment** | A named group of training runs (e.g., "fraud-detection-v2") | A CI pipeline / GitHub Actions workflow |
| **Run** | A single execution of training code | A single pipeline run / build |
| **Parameters** | Key-value inputs to training (learning_rate=0.01) | Environment variables / build args |
| **Metrics** | Numeric outputs measuring model quality (accuracy=0.94) | SLIs reported after a canary deploy |
| **Artifacts** | Files produced by a run (model.pkl, plots) | Build artifacts (Docker image, helm chart) |
| **Model Registry** | Central store for model versions with lifecycle stages | Container registry (ECR/Harbor/Artifactory) |

### Model Lifecycle Stages

```
None → Staging → Production → Archived
```

| Stage | Meaning | Ops equivalent |
|-------|---------|---------------|
| **None** | Just registered, not validated | Image pushed but not deployed anywhere |
| **Staging** | Under testing/validation | Deployed to staging environment |
| **Production** | Serving live traffic | Deployed to production |
| **Archived** | Retired, kept for audit | Old image tag kept in registry for compliance |

Transitions between stages are explicit, auditable events — just like a deploy approval in your CI/CD pipeline.

---

## The Mapping Table: ML ↔ Ops

This is the mental model to carry with you:

| ML Concept | Ops Concept You Know |
|-----------|---------------------|
| Model registry | Container registry (ECR, Harbor, Artifactory) |
| Registered model | Docker image repository |
| Model version | Image tag (v1.2.3, sha256:abc) |
| Experiment | CI/CD pipeline definition |
| Run | Pipeline execution / build |
| Parameters | Build arguments / env vars |
| Metrics | SLIs / post-deploy health checks |
| Artifacts | Build outputs |
| Model stage (staging/prod) | Deploy environment |
| Stage transition | Deployment promotion (with approval gate) |
| Experiment comparison | Comparing two canary deploys side-by-side |
| Rollback to previous model version | `kubectl rollout undo` |

---

## Key Takeaways

1. **Models are artifacts.** Treat them like container images: version, store, promote, roll back.
2. **Experiments are builds.** Every training run should be logged and reproducible.
3. **The registry is your source of truth.** It answers "what's in production right now?" for models.
4. **Reproducibility = code + data + params + env.** Miss any one and you can't rebuild.
5. **Stage transitions are deployments.** They should be gated, auditable, and reversible.

---

## Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow Quickstart](https://mlflow.org/docs/latest/quickstart.html)
- [ML Metadata & Lineage (Google)](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

## ✅ Week 4 Checklist

- [ ] I can explain why model versioning prevents "can't roll back" incidents
- [ ] I understand the three components of a model registry (artifact store, metadata, lifecycle)
- [ ] I can describe what experiment tracking captures (params, metrics, artifacts, env, code)
- [ ] I can map MLflow concepts to CI/CD equivalents I already use
- [ ] I've run the lab: trained models, logged experiments, compared runs
- [ ] I've registered a model, promoted it through stages, and performed a rollback
- [ ] I can explain why reproducibility requires code version + data version + hyperparams + environment
- [ ] I can articulate when my team should use a model registry vs. ad-hoc model storage
