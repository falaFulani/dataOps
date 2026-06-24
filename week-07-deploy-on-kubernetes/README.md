# Week 7: Deploy on Kubernetes (Your Strength)

> **This week should feel like home.** You run k8s clusters in production at the bank. The only new thing here is the payload type — an ML model instead of a Java service — and a few ML-specific operational considerations (model loading time, inference latency patterns, GPU scheduling). Enjoy the confidence boost.

## What's New (and What Isn't)

| You Already Know | What's ML-Specific |
|------------------|-------------------|
| Deployments, Services, Ingress | Model loading adds startup time (affects readiness probes) |
| HPA, resource limits, pod scheduling | Inference is CPU/memory-heavy, sometimes GPU; burst patterns differ |
| Canary deployments, traffic splitting | You're rolling out a **model version**, not just a code version |
| Helm charts, GitOps | Same tooling, different artifact (model file vs compiled binary) |
| Health checks, liveness/readiness | Readiness = "model loaded in memory", not just "process started" |

**Bottom line:** If you can deploy a Spring Boot service on k8s, you can deploy an ML model service. The manifests in this directory prove it.

---

## Model Serving on Kubernetes

### Why K8s Is the Production Standard for ML Serving

You already know why k8s wins for stateless services. The same reasons apply to ML inference:

- **Horizontal scaling** — inference pods are stateless (model loaded at startup, no session state)
- **Resource isolation** — ML workloads can be memory-hungry; limits prevent noisy-neighbor problems
- **Rolling updates** — deploy new model versions with zero downtime
- **Multi-tenancy** — multiple models/teams sharing a cluster, isolated by namespace
- **GPU scheduling** — k8s can schedule pods on GPU nodes via device plugins and node selectors
- **Observability** — Prometheus, standard pod metrics, custom metrics — same stack you already run

### ML Services Are Just Services (With Some Quirks)

| Characteristic | Typical Microservice | ML Inference Service |
|----------------|---------------------|---------------------|
| Startup time | 2-10 seconds | 10-60+ seconds (model loading) |
| Memory profile | Moderate, stable | High at startup, stable during serving |
| CPU pattern | Request-proportional | Can spike during inference (batch predictions) |
| Statefulness | Stateless | Stateless (model in memory, not mutated) |
| Scaling trigger | CPU/RPS | CPU/RPS + inference latency + queue depth |
| Rollout risk | Logic bugs | Silent accuracy degradation (no error, just wrong) |

---

## KServe and Seldon Core

These are Kubernetes-native ML serving platforms. They sit on top of plain k8s and add ML-specific capabilities.

### What They Add on Top of Plain K8s Deployments

| Capability | Plain K8s | KServe/Seldon |
|-----------|-----------|---------------|
| Model serving | You write the FastAPI app | Pre-built model servers (TF Serving, Triton, SKLearn) |
| Autoscaling | HPA on CPU/memory | Scale-to-zero, scale on inference RPS |
| Canary rollouts | Manually configure Istio/Linkerd | Built-in traffic splitting per model version |
| Multi-model serving | One pod = one model | Multiple models per pod (resource efficiency) |
| A/B testing | Manual routing | Declarative traffic split |
| Model transformers | Write pre/post processing code | Pluggable transformer containers (pre/post-processing sidecars) |
| Explainability | Not built in | Optional explainer containers |
| Monitoring | Roll your own Prometheus metrics | Built-in payload logging, drift detection hooks |

### KServe (formerly KFServing)

KServe is the Kubernetes-native standard for model serving. It's part of the Kubeflow ecosystem.

```yaml
# This is the entire manifest to serve a model on KServe
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: iris-classifier
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://my-bucket/models/iris/v1"
```

That's it. KServe handles:
- Pulling the model from storage
- Running it on a pre-built sklearn serving image
- Creating the k8s Deployment, Service, and Ingress
- Autoscaling (including scale-to-zero with Knative)
- Readiness based on model load status

**When to use KServe:** When you want a standardized, declarative way to serve models without writing serving code. Good for teams with many models.

### Seldon Core

Seldon Core takes a graph-based approach — you define an inference graph with pre-processing, prediction, and post-processing nodes.

```yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: iris-model
spec:
  predictors:
  - graph:
      name: classifier
      implementation: SKLEARN_SERVER
      modelUri: "gs://my-bucket/models/iris"
    name: default
    replicas: 3
    traffic: 100
```

**When to use Seldon:** When you need complex inference graphs (pre-processing → model → post-processing), or A/B testing and multi-armed bandit routing between model versions.

### Should You Use KServe/Seldon or Plain K8s?

| Scenario | Recommendation |
|----------|---------------|
| 1-3 models, team knows k8s well | Plain k8s (like this week's lab) — less complexity |
| 10+ models, multiple teams | KServe — standardized, declarative, less custom code |
| Complex inference pipelines | Seldon — inference graph model is purpose-built for this |
| Need scale-to-zero | KServe (uses Knative under the hood) |
| Strict control over infrastructure | Plain k8s — you own every layer |

**For your bank:** Start with plain k8s deployments (you already know how). Evaluate KServe when the ML team scales beyond 5-10 models and needs self-service deployment.

---

## Autoscaling Inference Workloads

### HPA for ML — What's Different

You run HPA already. For ML workloads, the considerations shift slightly:

| Dimension | Traditional Service | ML Inference |
|-----------|-------------------|--------------|
| CPU scaling | Works well | Works, but inference can be bursty — set target lower (60-70%) |
| Memory scaling | Rarely needed | Model in memory is constant; memory HPA less useful |
| Custom metrics | RPS, queue depth | Inference latency p99, prediction queue depth, GPU utilization |
| Scale-up time | Fast (seconds) | Slow (model loading = 10-60s before pod is ready) |
| Min replicas | 1-2 | 2+ (cold start penalty means you can't scale from zero quickly) |

### GPU Considerations

If your ML team eventually needs GPU inference:

```yaml
resources:
  limits:
    nvidia.com/gpu: 1  # Request 1 GPU
  requests:
    nvidia.com/gpu: 1
```

- GPUs are **not** fractionally schedulable by default (1 pod = 1 GPU minimum)
- GPU nodes are expensive → right-size aggressively, consider time-sharing (MIG on A100s)
- Many models run fine on CPU — only use GPU for large models (LLMs, image models)
- For your Iris classifier: CPU is more than enough. Don't over-engineer.

### Request-Based Scaling (Custom Metrics)

The most useful custom metric for ML services is **inference requests per second**:

```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: inference_requests_per_second
    target:
      type: AverageValue
      averageValue: "100"  # Scale when avg pod exceeds 100 req/s
```

This requires the Prometheus Adapter (or KEDA) to expose custom metrics to the HPA. You likely already have this pattern for other services.

---

## Canary Deployments for Models

### Why Canaries Matter More for ML

When you canary a traditional service, you watch for:
- Error rates (5xx)
- Latency spikes
- Functional correctness

When you canary a model, you also watch for:
- **Prediction distribution shift** — is the new model predicting differently?
- **Confidence score changes** — is the new model less confident?
- **Business metric impact** — are fraud alerts going up/down? Are loan approvals changing?

The insidious thing about model bugs: they don't throw errors. They just silently produce bad predictions. Canaries with metric comparison are your safety net.

### Traffic Splitting Approaches

| Approach | Tool | Complexity |
|----------|------|-----------|
| Weighted routing | Istio/Linkerd VirtualService | Low (you know this) |
| Header-based routing | Ingress annotations | Low |
| KServe canary | Built-in traffic field | Very low |
| Seldon A/B | Built-in predictor weights | Very low |

The `canary-deployment.yaml` in this directory shows the basic approach with NGINX Ingress annotations. In production at the bank, you'd use Istio since you likely already have it.

---

## Resource Considerations for ML Inference

### ML Inference Is CPU/Memory Heavy

| Resource | Typical ML Service | Why |
|----------|-------------------|-----|
| Memory | 512Mi - 4Gi | Model artifact loaded into RAM |
| CPU | 500m - 2000m | Inference is computation (matrix multiplication) |
| GPU | Optional | Only for large models (transformers, image models) |
| Disk | Minimal at runtime | Model loaded at startup, not streamed |
| Network | Low | Payloads are small (feature vectors → predictions) |

### Sizing Guidelines

For your Iris classifier (simple sklearn model):
- `requests: {cpu: 250m, memory: 256Mi}` — model is tiny
- `limits: {cpu: 500m, memory: 512Mi}` — headroom for bursts

For a production fraud detection model (gradient boosting, larger features):
- `requests: {cpu: 500m, memory: 1Gi}`
- `limits: {cpu: 1000m, memory: 2Gi}`

For a large language model (if your bank goes there):
- `requests: {cpu: 4000m, memory: 16Gi}` or GPU
- `limits: {cpu: 8000m, memory: 32Gi}`

**Rule of thumb:** Profile your model's inference latency under load, then set requests at the steady-state resource usage and limits at 2x for burst headroom.

---

## Mapping to Your Existing K8s Expertise

| This Week's Task | Your Existing Equivalent |
|-----------------|--------------------------|
| Write a Deployment manifest | Same as every deployment you've ever written |
| Configure readiness probe | Same, but with higher `initialDelaySeconds` for model loading |
| Set resource requests/limits | Same, but profile for ML workload characteristics |
| Create HPA | Same, potentially with custom metrics for inference RPS |
| Configure Ingress | Identical |
| Set up canary | Same Istio/Linkerd patterns you already use |
| Anti-affinity rules | Identical — spread inference pods across nodes |

**New patterns to note:**
1. `initialDelaySeconds` on readiness probes should be generous (30-120s for large models)
2. Resource limits need to account for model size in memory (not just application overhead)
3. `terminationGracePeriodSeconds` should allow in-flight inference requests to complete

---

## Lab: Deploy the Model Service to Local K8s

### What You're Deploying

The FastAPI model service from Week 5, packaged for Kubernetes:

```
┌─────────────────────────────────────────────────────────┐
│  Kind/Minikube Cluster                                  │
│                                                         │
│  ┌─────────────┐     ┌───────────────────────────────┐  │
│  │   Ingress   │────▶│  Service (ClusterIP :80)      │  │
│  │  (NGINX)    │     │          │                    │  │
│  └─────────────┘     └──────────┼────────────────────┘  │
│                                 │                        │
│                    ┌────────────┼────────────┐           │
│                    ▼            ▼            ▼           │
│              ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│              │  Pod 1   │ │  Pod 2   │ │  Pod 3   │     │
│              │ model:v1 │ │ model:v1 │ │ model:v1 │     │
│              └──────────┘ └──────────┘ └──────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │  HPA: scale 2-10 pods based on CPU (70%)           ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Quick Start

```bash
# 1. Verify prerequisites
chmod +x setup.sh && ./setup.sh

# 2. Deploy to local cluster
chmod +x deploy.sh && ./deploy.sh

# 3. Test the endpoint
curl http://model.local/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This guide |
| `k8s/deployment.yaml` | Deployment with probes, resources, anti-affinity |
| `k8s/service.yaml` | ClusterIP Service |
| `k8s/hpa.yaml` | HorizontalPodAutoscaler |
| `k8s/ingress.yaml` | Ingress for external access |
| `k8s/canary-deployment.yaml` | Canary deployment with traffic splitting |
| `k8s/kserve-example.yaml` | KServe InferenceService example (for reference) |
| `setup.sh` | Verify prerequisites |
| `deploy.sh` | Deploy to local kind/minikube cluster |

---

## Resources

| Resource | Why |
|----------|-----|
| [KServe Documentation](https://kserve.github.io/website/) | The k8s-native ML serving standard |
| [Seldon Core Documentation](https://docs.seldon.io/projects/seldon-core/en/latest/) | Alternative ML serving platform, graph-based |
| [KServe GitHub Examples](https://github.com/kserve/kserve/tree/master/docs/samples) | Practical InferenceService examples |
| [Kubernetes HPA Custom Metrics](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/#autoscaling-on-multiple-metrics-and-custom-metrics) | For inference-RPS-based scaling |
| [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/overview.html) | If you need GPU scheduling |
| [Istio Traffic Management](https://istio.io/latest/docs/tasks/traffic-management/) | Canary deployments you already know |
| [KEDA](https://keda.sh/) | Event-driven autoscaling (alternative to custom metrics HPA) |

---

## Week 7 Checklist

- [ ] Read this README — identify what's genuinely new vs. what you already know
- [ ] Run `setup.sh` to verify prerequisites (kubectl, kind/minikube, docker)
- [ ] Run `deploy.sh` to deploy the model service to a local cluster
- [ ] Verify the deployment: `kubectl get pods,svc,hpa,ingress -n ml-serving`
- [ ] Test the prediction endpoint via Ingress or port-forward
- [ ] Review `canary-deployment.yaml` — compare to how you'd canary any other service
- [ ] Review `kserve-example.yaml` — understand what KServe adds vs plain k8s
- [ ] Experiment: scale the deployment manually, watch the HPA react
- [ ] Think about: How would you integrate this into your bank's existing GitOps workflow?
- [ ] Think about: What Prometheus metrics would you alert on for an ML service vs a regular service?
- [ ] Think about: When would KServe/Seldon be worth the added complexity for your team?

---

## Key Takeaways

1. **This is k8s.** You already know how to do this. The manifests are standard.
2. **Model loading time is the main difference** — set readiness probes generously, expect slower cold starts.
3. **KServe/Seldon add value at scale** — 10+ models, self-service for data scientists, standardized deployment.
4. **Canaries for models need ML metrics** — prediction distribution, not just error rates.
5. **Start simple.** Plain k8s Deployments + your existing Istio/Linkerd for traffic management. Add KServe when the team outgrows manual manifests.
