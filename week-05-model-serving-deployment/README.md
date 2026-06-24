# Week 5: Model Serving & Deployment

> **Key insight:** You already know Docker and APIs. This is deploying a slightly unusual service where the business logic is a model file instead of application code.

## What Changes (and What Doesn't)

Think about every microservice you've deployed at the bank. They all follow the same pattern:
- Container image → deployed to Kubernetes → exposed via service → monitored

An ML service is identical, except:
- The "business logic" is a serialized model file (`.pkl`, `.onnx`, `.pt`) instead of compiled code
- The input/output contract is numerical features → predictions instead of JSON → JSON
- You need to version the **model artifact** separately from the **application code**

Everything else — networking, scaling, health checks, rollout strategies — is the same infrastructure you manage today.

---

## Real-Time Inference vs Batch Inference

### Real-Time (Online) Inference

The model sits behind an API. Request comes in, prediction goes out. Low latency matters.

| Aspect | Details |
|--------|---------|
| **Pattern** | Client → API Gateway → Model Service → Response |
| **Latency** | Typically < 100ms p99 |
| **Use cases** | Fraud detection at transaction time, credit scoring during application, chatbot responses |
| **Infrastructure** | Always-on pods, autoscaling based on RPS, load balancing |
| **Your mental model** | Same as any stateless API service you run today |

```
POST /predict
{
  "features": [5.1, 3.5, 1.4, 0.2]
}

Response:
{
  "prediction": "setosa",
  "confidence": 0.97,
  "model_version": "iris-v1.2.0",
  "latency_ms": 12
}
```

### Batch Inference

The model processes a large dataset on a schedule. Throughput matters, latency doesn't.

| Aspect | Details |
|--------|---------|
| **Pattern** | Scheduler → Job → Read data → Run predictions → Write results |
| **Latency** | Minutes to hours (acceptable) |
| **Use cases** | Monthly risk scoring of all accounts, daily churn predictions, overnight report generation |
| **Infrastructure** | CronJobs, Spark jobs, or Airflow DAGs |
| **Your mental model** | Same as any batch ETL job you schedule today |

### When to Use Which

| Signal | Real-Time | Batch |
|--------|-----------|-------|
| Decision needed immediately | ✅ | ❌ |
| Processing millions of records | ❌ | ✅ |
| User is waiting for response | ✅ | ❌ |
| Results can be pre-computed | ❌ | ✅ |
| Cost sensitivity (GPU) | Higher | Lower (spot instances) |
| Freshness requirement | Up-to-the-second | Hours/days old is fine |

**Banking examples:**
- Real-time: Fraud check on card swipe, instant credit decision
- Batch: Monthly portfolio risk assessment, overnight AML screening of all transactions

---

## Model Deployment Patterns

### The Mapping Table: What You Already Know

| DevOps Pattern | ML Equivalent | What's Different |
|---------------|---------------|-----------------|
| **Canary deployment** | Canary model rollout | Same. Route 5% traffic to new model, watch error rates |
| **Blue-Green** | Blue-Green model swap | Same. Two model versions running, switch traffic instantly |
| **Shadow/Dark launch** | Shadow model scoring | Same. New model receives traffic but responses aren't used |
| **A/B testing** | A/B model testing | Similar, but you're measuring **prediction quality**, not just uptime |
| **Feature flags** | Model version flags | Same. Gate which model version serves which customers |
| **Rolling update** | Rolling model update | Same. Gradually replace old model pods with new ones |

### Canary Deployment for Models

```yaml
# You'd do this in Istio/Linkerd — same as any canary
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  http:
  - route:
    - destination:
        host: model-service
        subset: v1
      weight: 95
    - destination:
        host: model-service
        subset: v2-candidate
      weight: 5
```

**What to watch during canary:**
- Standard: latency, error rate, 5xx responses (same as always)
- ML-specific: prediction distribution shift, confidence score changes, business metric impact

### Shadow (Dark Launch) for Models

Perfect for ML because you can compare predictions without risk:

```
Request → Model v1 (serves response to user)
       → Model v2 (logs prediction, discarded)

Compare: Do v1 and v2 agree? Where do they disagree? Is v2 better?
```

This is the safest pattern for banking. Zero customer impact while you validate the new model.

### A/B Testing for Models

Unlike traditional A/B testing (button color, UI layout), model A/B testing measures:
- Does Model B produce better **business outcomes**? (fewer false fraud alerts, better credit decisions)
- This requires longer evaluation windows — you might need weeks to measure loan default rates

---

## What a Model Serving Endpoint Looks Like

### Input Schema → Prediction → Confidence

Every model serving endpoint follows this contract:

```
┌─────────────────────────────────────────────────────┐
│  REQUEST                                            │
│  ─────────                                          │
│  {                                                  │
│    "features": {                                    │
│      "sepal_length": 5.1,                          │
│      "sepal_width": 3.5,                           │
│      "petal_length": 1.4,                          │
│      "petal_width": 0.2                            │
│    }                                               │
│  }                                                  │
├─────────────────────────────────────────────────────┤
│  MODEL (black box)                                  │
│  ─────                                              │
│  Loads weights from model.pkl                       │
│  Transforms input → numpy array                     │
│  Runs inference                                     │
├─────────────────────────────────────────────────────┤
│  RESPONSE                                           │
│  ────────                                           │
│  {                                                  │
│    "prediction": "setosa",                         │
│    "confidence": 0.97,                             │
│    "probabilities": {                              │
│      "setosa": 0.97,                               │
│      "versicolor": 0.02,                           │
│      "virginica": 0.01                             │
│    },                                              │
│    "model_version": "1.2.0",                       │
│    "prediction_id": "uuid-for-audit"               │
│  }                                                  │
└─────────────────────────────────────────────────────┘
```

**Why confidence matters in banking:**
- Confidence < threshold → route to human reviewer
- Confidence tracking over time → detect model degradation
- Audit trail → every prediction logged with ID for compliance

---

## Health Checks for ML Services

### Standard Health Checks (You Know These)

| Check | Purpose | ML Service Implementation |
|-------|---------|--------------------------|
| **Liveness** (`/healthz`) | "Is the process alive?" | Same as always — returns 200 if the process is running |
| **Readiness** (`/ready`) | "Can it serve traffic?" | Model loaded in memory + dependencies available |

### ML-Specific Health: Model Quality Check

This is the new one. Beyond "is it running?", you need "is it still accurate?"

| Check | What It Measures | Example |
|-------|-----------------|---------|
| **Model loaded** | Is the model artifact in memory? | Fail readiness if model file missing/corrupt |
| **Prediction distribution** | Are outputs still in expected range? | Alert if 90% of predictions are suddenly one class |
| **Feature drift** | Are inputs still in the training distribution? | Alert if input features look nothing like training data |
| **Latency budget** | Is inference fast enough? | Mark unhealthy if p99 > SLO threshold |

```python
@app.get("/health")
def health_check():
    """Liveness — is the service running?"""
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    """Readiness — can we serve predictions?"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model_version": MODEL_VERSION}
```

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 15

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 30  # Models take longer to load than typical services
  periodSeconds: 10
```

**Note:** `initialDelaySeconds` for readiness is typically higher for ML services because loading a large model into memory takes time (seconds to minutes depending on model size).

---

## This Week's Lab

You'll build and deploy a complete model serving endpoint:

1. Train a simple model (Iris classifier) and save it as a `.pkl` file
2. Wrap it in a FastAPI application with proper endpoints
3. Containerize it with a production-ready Dockerfile
4. Test the full request/response cycle

### Files in This Directory

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI model serving application |
| `app/model_training.py` | Script to train and save a model |
| `Dockerfile` | Production container for the model service |
| `docker-compose.yml` | Local development setup |
| `test_api.sh` | curl commands to test all endpoints |
| `setup.sh` | Install Python dependencies |

### Quick Start

```bash
# 1. Install dependencies
chmod +x setup.sh && ./setup.sh

# 2. Train and save the model
python app/model_training.py

# 3. Run the service locally
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Test it (in another terminal)
chmod +x test_api.sh && ./test_api.sh

# Or with Docker:
docker-compose up --build
./test_api.sh
```

---

## Resources

| Resource | Why It's Useful |
|----------|-----------------|
| [FastAPI Documentation](https://fastapi.tiangolo.com/) | Framework used for the model API |
| [MLflow Model Serving](https://mlflow.org/docs/latest/models.html) | Production model serving at scale |
| [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/) | Kubernetes-native model serving (you'll appreciate the K8s integration) |
| [BentoML](https://docs.bentoml.com/) | Framework for packaging and serving models |
| [KServe (formerly KFServing)](https://kserve.github.io/website/) | Serverless inference on Kubernetes |
| [Google ML Best Practices - Serving](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) | Enterprise ML serving patterns |

---

## Week 5 Checklist

- [ ] Read through this README and identify patterns you already use
- [ ] Run `setup.sh` to install dependencies
- [ ] Train the model with `python app/model_training.py`
- [ ] Start the FastAPI server and test with `test_api.sh`
- [ ] Build and run the Docker container
- [ ] Review the Dockerfile — note what's different from your typical service containers (probably nothing)
- [ ] Think about: How would you canary-deploy this in your bank's Kubernetes clusters?
- [ ] Think about: What SLOs would you set for a fraud detection model endpoint?
- [ ] Think about: Where does the model `.pkl` file come from in a real CI/CD pipeline? (Hint: model registry — Week 6 topic)

---

## Key Takeaways

1. **Model serving is just API serving** — you already know how to do this
2. **The model file is the new artifact** — version it, store it, deploy it like any other build output
3. **Confidence scores are your new error rates** — track them like you track SLIs
4. **Shadow deployments are your best friend** — especially in banking where wrong predictions have real cost
5. **Health checks need an ML dimension** — "running" isn't enough, "producing reasonable predictions" is the real readiness signal
