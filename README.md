# MLOps Engineering Course — Tailored for Alex

A 12-week, hands-on course designed for an engineer who already owns
**platform engineering, SLOs, incident governance, Kubernetes, and team leadership**.
It deliberately skips general DevOps/ops fundamentals you already have and
front-loads the **ML-specific layer** that's new to you.

**Goal:** Become operationally fluent in MLOps — enough to lead an MLOps support
team, harden ML alerting, and own ML incident response — then deepen into the
build side for long-term career growth.

---

## How to use this course

- Each week has: **concepts**, **hands-on lab**, and a **"connect to your ops background"** note.
- Time budget: ~6–8 hrs/week. Compress to 6 weeks by doubling up if you have time.
- Track your progress with the checkboxes.
- The capstone (Weeks 11–12) is portfolio-worthy — put it on your CV/GitHub.

**Legend:** 🧠 Concept · 🛠️ Lab · 🔗 Maps to your existing skills · 📚 Resource

---

## Phase 0 — Orientation (before Week 1)

Skim these so the vocabulary stops feeling foreign. Don't study deeply yet.

- [ ] 📚 Read Google's "MLOps: Continuous delivery and automation pipelines in ML" (the MLOps maturity levels 0/1/2 article)
- [ ] 📚 Read "Rules of Machine Learning" by Martin Zinkevich (ops-focused, no math)
- [ ] 🔗 Write one page mapping your current ops responsibilities to ML equivalents (SLOs → ML SLOs, incidents → drift events, etc.)

---

## PHASE 1 — ML FOUNDATIONS FOR OPERATORS (Weeks 1–3)

Enough ML to be dangerous and credible. You are NOT becoming a data scientist —
you're learning what the team operates so you can support and lead it.

### Week 1 — How ML actually works (just enough)
- 🧠 Supervised vs unsupervised learning; training vs inference; what a "model" and a "feature" really are
- 🧠 The ML lifecycle end-to-end: data → train → evaluate → deploy → monitor → retrain
- 🧠 Why ML fails *silently* (the core operator insight)
- 🛠️ Train a simple model (scikit-learn) on a public dataset in a notebook. Don't optimize it — just feel the workflow: load data, fit, predict, measure accuracy.
- 🔗 Compare this lifecycle to a software release lifecycle you already run.
- 📚 "Machine Learning for Everybody" (freeCodeCamp, video) or Andrew Ng's intro — watch at 1.5x, skip the math derivations.

### Week 2 — Data is the product
- 🧠 Data quality, schema validation, feature engineering, train/test splits
- 🧠 Training-serving skew (why prod data processing must match training)
- 🛠️ Use a data validation tool (Great Expectations or `pandas` checks) to write data quality rules: no nulls, value ranges, schema match. This is your future alerting layer.
- 🔗 This is the ML version of input validation and health checks you already design.

### Week 3 — Model evaluation & the drift family
- 🧠 Accuracy, precision, recall, F1 — what each means and when each matters
- 🧠 **Data drift, concept drift, prediction drift, training-serving skew** (learn these cold — they're your incident categories)
- 🛠️ Use **Evidently AI** to generate a drift report comparing two data slices. This is the single most relevant tool for an MLOps support lead.
- 🔗 Drift = a new class of "incident" with no error log. Map each drift type to a hypothetical alert and runbook.

**Milestone 1:** Write a 1-page "ML failure modes" runbook draft in your own words.

---

## PHASE 2 — THE MLOps PLATFORM (Weeks 4–7)

Now you build the operational tooling. This is your home turf, extended.

### Week 4 — Experiment tracking & model registry
- 🧠 Why model versioning matters; what a model registry is; reproducibility
- 🛠️ Set up **MLflow** locally. Log experiments, register a model, promote it through stages (staging → production), and roll back to a prior version.
- 🔗 A model registry is artifact versioning + rollback — exactly like deploy versioning you already do.

### Week 5 — Model serving & deployment patterns
- 🧠 Real-time (API) vs batch inference; canary, shadow, blue-green for models
- 🛠️ Wrap your Week 1 model in a **FastAPI** service, containerize it with Docker, expose a `/predict` endpoint and a `/health` check.
- 🔗 You already know Docker and k8s. This is deploying a slightly unusual service. Reuse your instincts.

### Week 6 — Pipelines & orchestration
- 🧠 What an ML pipeline orchestrator does; DAGs; scheduled retraining
- 🛠️ Build a simple pipeline that chains: validate data → train → evaluate → register. Use a lightweight tool (Prefect or ZenML; or Kubeflow Pipelines if you want the k8s-native one).
- 🔗 This is workflow automation / CI-for-models. Same governance instincts as your deploy pipelines.

### Week 7 — Deploy on Kubernetes (your strength)
- 🧠 Model serving on k8s; KServe / Seldon Core basics; autoscaling inference
- 🛠️ Deploy your FastAPI model to a local k8s cluster (kind/minikube). Add a readiness probe, resource limits, and an HPA.
- 🔗 This week should feel easy and confidence-building — it's mostly k8s with an ML payload.

**Milestone 2:** You have a model that's trained, versioned, served on k8s, and reproducible. Push it to GitHub.

---

## PHASE 3 — MONITORING, RELIABILITY & GOVERNANCE (Weeks 8–10)

The heart of the **support lead** role. Lean hard on your SLO and incident experience here.

### Week 8 — ML observability
- 🧠 Two monitoring layers: operational (latency/errors/throughput) + ML-specific (drift/accuracy/data quality)
- 🛠️ Instrument your served model with **Prometheus + Grafana** for operational metrics, and **Evidently** (or Arize/WhyLabs free tier) for drift/quality. Build one dashboard showing both layers.
- 🔗 You already build SLO dashboards. Add the ML row to the dashboard you'd build anyway.

### Week 9 — ML SLOs & alerting frameworks
- 🧠 Defining SLOs for ML systems (availability + prediction-quality SLOs); error budgets for models; alerting on drift burn-rate, not noise
- 🛠️ Define 3–4 SLOs for your model service and configure alerts (e.g., latency > X, drift score > threshold, data-quality check failures). Tune to avoid noise.
- 🔗 This is literally the "harden our alerting frameworks" line from the job description. This week IS the job.

### Week 10 — ML incident response & governance
- 🧠 ML incident categories; the retraining decision (when to retrain vs rollback vs investigate data); blameless postmortems for ML; model governance, lineage, and audit (your banking edge)
- 🛠️ Write a full ML incident runbook + postmortem template: "Model accuracy dropped overnight" — triage steps, who to involve, rollback vs retrain decision tree.
- 🔗 Directly extends your post-incident governance work. This is where your banking/regulatory background becomes a differentiator, not a gap.

**Milestone 3:** A complete ML on-call runbook + SLO definitions + postmortem template. This is a portfolio piece *and* something you could pitch to use at CloudFactory.

---

## PHASE 4 — CAPSTONE (Weeks 11–12)

Build one end-to-end project that demonstrates the whole loop. Put it on GitHub
with a clear README — this becomes interview evidence.

### The capstone project
Build a small but complete MLOps system:
1. A trained, versioned model (MLflow)
2. Served via API, containerized, deployed on k8s
3. A retraining pipeline (orchestrated)
4. Full monitoring: operational + drift/quality dashboards
5. Defined SLOs + alerting
6. An incident runbook + postmortem template
7. A README explaining the architecture and operational design decisions

- [ ] Week 11 — Build and integrate the pieces from Phases 2–3 into one repo
- [ ] Week 12 — Documentation, architecture diagram, runbook, and a short demo video/walkthrough

**Capstone framing for interviews:** "I built an end-to-end MLOps system focused on
the operational layer — versioning, serving, monitoring, SLOs, and incident response —
to ground my reliability and governance experience in ML-specific tooling."

---

---

## PHASE 5 — HIGH PRIORITY EXTENSIONS (Weeks 13–16)

Topics that directly map to the CloudFactory role and modern MLOps leadership.
Do these immediately after the capstone.

### Week 13 — Data Labeling & Annotation (CloudFactory's Core Business)
- 🧠 Labeling workflows: task design, quality assurance, inter-annotator agreement
- 🧠 Active learning: using model uncertainty to prioritize what gets labeled next
- 🧠 Human-in-the-loop ML: when and how humans stay in the prediction loop
- 🧠 Labeling platforms: Label Studio, Labelbox, Scale AI, Prodigy
- 🛠️ Set up **Label Studio** locally. Create an annotation project, label a small dataset, export for training.
- 🛠️ Implement a simple active learning loop: train → identify uncertain samples → queue for labeling → retrain
- 🔗 This IS CloudFactory's business. Understanding it shows domain fluency, not just ops fluency.
- 📚 [Prodigy annotation docs](https://prodi.gy/) · [Human-in-the-loop ML (Robert Monarch)](https://www.manning.com/books/human-in-the-loop-machine-learning)

### Week 14 — Feature Stores
- 🧠 What a feature store solves: feature reuse, online/offline consistency, training-serving skew elimination
- 🧠 Online vs offline feature serving (real-time lookups vs batch training joins)
- 🧠 Feature computation, storage, and retrieval patterns
- 🧠 Tools: Feast (open-source), Tecton, Hopsworks, Vertex AI Feature Store
- 🛠️ Set up **Feast** locally. Define features, materialize them, serve them to your model from Week 5.
- 🛠️ Demonstrate how a feature store eliminates training-serving skew by using the same transformation in both paths.
- 🔗 This is the infrastructure that eliminates the #1 ML production failure mode (skew). Your territory.
- 📚 [Feast docs](https://docs.feast.dev/) · [Feature Store for ML (Chip Huyen)](https://www.featurestore.org/)

### Week 15 — LLMOps (Generative AI Operations)
- 🧠 How LLM serving differs: prompt engineering, context windows, token costs, latency profiles
- 🧠 RAG (Retrieval-Augmented Generation) pipelines: embedding, vector stores, retrieval, generation
- 🧠 LLM evaluation: how do you measure quality when there's no single "correct" answer?
- 🧠 Prompt management and versioning (prompt registries)
- 🧠 Fine-tuning workflows vs prompt engineering vs RAG (when to use which)
- 🧠 Cost management: token budgets, caching, model routing (small model for easy, large for hard)
- 🛠️ Build a simple **RAG pipeline**: embed documents → store in a vector DB (ChromaDB) → query with an LLM → evaluate output quality.
- 🛠️ Instrument with token cost tracking and latency monitoring.
- 🔗 Same operational patterns (monitoring, SLOs, incident response) but new failure modes: hallucination, prompt injection, cost overrun.
- 📚 [LangChain docs](https://docs.langchain.com/) · [LlamaIndex](https://docs.llamaindex.ai/) · [OpenAI best practices](https://platform.openai.com/docs/guides)

### Week 16 — Chaos Engineering for ML
- 🧠 Why chaos engineering applies to ML: test your monitoring and response under controlled failure
- 🧠 ML-specific chaos scenarios: inject drift, corrupt features, serve stale model, kill feature store
- 🧠 Game days: simulated ML incidents with the team (practice your runbooks)
- 🧠 Resilience testing: does your system gracefully degrade when components fail?
- 🛠️ Build a **chaos experiment suite**: scripts that inject data drift, drop features to null, swap model versions, introduce latency spikes.
- 🛠️ Run each experiment against your capstone system and verify that your alerting catches it.
- 🛠️ Conduct a tabletop game day using your runbooks.
- 🔗 You may have done chaos engineering for services (Chaos Monkey, Litmus). Same principle, new failure injections.
- 📚 [Principles of Chaos Engineering](https://principlesofchaos.org/) · [Gremlin ML chaos patterns](https://www.gremlin.com/)

**Milestone 4:** Your capstone system survives chaos experiments. Alerting fires correctly. Runbooks work under pressure.

---

## PHASE 6 — MEDIUM PRIORITY (Weeks 17–21)

Deepen platform skills and expand into areas relevant to growth as an MLOps leader.

### Week 17 — ML on Cloud Platforms (AWS/GCP/Azure)
- 🧠 Managed MLOps services: SageMaker (AWS), Vertex AI (GCP), Azure ML
- 🧠 What managed platforms give you vs. self-managed (trade-offs: cost, control, vendor lock-in)
- 🧠 Comparison matrix: when to use managed vs. open-source tools
- 🧠 Multi-cloud ML strategy considerations
- 🛠️ Deploy your model on **SageMaker** or **Vertex AI** (free tier). Compare the experience to your self-built stack.
- 🛠️ Set up endpoint monitoring using the platform's native tools (CloudWatch for SageMaker, Cloud Monitoring for Vertex).
- 🔗 You already manage cloud infrastructure. This is understanding the ML-specific managed services layer.
- 📚 [SageMaker docs](https://docs.aws.amazon.com/sagemaker/) · [Vertex AI docs](https://cloud.google.com/vertex-ai/docs)

### Week 18 — Model Explainability (Hands-on SHAP/LIME)
- 🧠 Why explainability matters: regulatory requirements, debugging, stakeholder trust
- 🧠 SHAP values: global vs local explanations, feature importance
- 🧠 LIME: local surrogate models for individual predictions
- 🧠 When to use which method; limitations of each
- 🧠 Serving explanations: adding a `/explain` endpoint alongside `/predict`
- 🛠️ Add **SHAP** explanations to your fraud model. Generate feature importance plots.
- 🛠️ Build an `/explain` endpoint that returns SHAP values for individual predictions.
- 🛠️ Create a "model explanation dashboard" panel in Grafana.
- 🔗 In banking, regulators require you to explain why a loan was denied. This is the tooling that enables it.
- 📚 [SHAP docs](https://shap.readthedocs.io/) · [LIME paper](https://arxiv.org/abs/1602.04938) · [Interpretable ML book (Molnar)](https://christophm.github.io/interpretable-ml-book/)

### Week 19 — GPU Infrastructure & Cost Optimization
- 🧠 GPU types and when you need them: V100, A100, T4, H100 — training vs inference
- 🧠 Fractional GPU sharing: MIG (Multi-Instance GPU), time-slicing, vGPU
- 🧠 Spot/preemptible instances for training (3-5x cost savings)
- 🧠 Inference cost optimization: batching, model distillation, quantization, caching
- 🧠 Cost allocation and chargeback for ML workloads
- 🛠️ Profile your model's inference cost. Calculate cost-per-prediction.
- 🛠️ Implement **request batching** for your inference endpoint (collect N requests, predict together).
- 🛠️ Set up a cost dashboard: cost per training run, cost per 1000 predictions, GPU utilization %.
- 🔗 You already manage infrastructure costs. ML adds GPU pricing complexity and training burst patterns.
- 📚 [NVIDIA GPU Operator on k8s](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/) · [ML cost optimization (AWS)](https://aws.amazon.com/blogs/machine-learning/)

### Week 20 — Multi-Model Serving & A/B Testing
- 🧠 Model routers: routing requests to different models based on context
- 🧠 A/B testing infrastructure: statistical significance, experiment design, metric selection
- 🧠 Multi-armed bandits: dynamically routing traffic to the best-performing model
- 🧠 Shadow scoring at scale: running N models in parallel for comparison
- 🧠 Per-model SLOs: managing reliability across a fleet of models
- 🛠️ Deploy **two model versions** with traffic splitting. Implement statistical comparison of their predictions.
- 🛠️ Build a **model router** that sends traffic based on request attributes (e.g., high-value customers → model A, others → model B).
- 🔗 You already do canary deploys. This extends to running multiple models long-term for experimentation.
- 📚 [Seldon A/B testing](https://docs.seldon.io/) · [Multi-armed bandits for ML (Google)](https://cloud.google.com/blog/products/ai-machine-learning/)

### Week 21 — Data Versioning & Lineage
- 🧠 Why datasets need versioning: reproducibility, audit, debugging model regressions
- 🧠 Tools: DVC (Data Version Control), LakeFS, Delta Lake, Pachyderm
- 🧠 Data lineage tracking: where did this data come from? What transformations were applied?
- 🧠 Tools: Apache Atlas, Amundsen, DataHub, OpenLineage
- 🧠 Integration with ML pipelines: connecting data versions to model versions
- 🛠️ Set up **DVC** on your capstone project. Version a dataset, make changes, track history.
- 🛠️ Implement **OpenLineage** integration in your Prefect pipeline to track data flow.
- 🔗 You version code (git) and containers (tags). Now version the third input: data.
- 📚 [DVC docs](https://dvc.org/doc) · [LakeFS docs](https://docs.lakefs.io/) · [OpenLineage](https://openlineage.io/)

**Milestone 5:** You can manage multiple models in production, explain their decisions, optimize costs, and track full data lineage.

---

## PHASE 7 — ADVANCED TOPICS (Weeks 22–27)

For long-term career growth. These take you from operational leadership into strategic MLOps architecture.

### Week 22 — Deep Learning & Neural Network Operations
- 🧠 How neural networks differ operationally: GPU requirements, longer training, larger artifacts
- 🧠 Training infrastructure: distributed training, checkpointing, experiment tracking at scale
- 🧠 Serving considerations: model compilation (TensorRT, ONNX), batching, GPU memory management
- 🧠 Frameworks: PyTorch, TensorFlow/Keras — understand the ecosystem
- 🛠️ Train a simple neural network (PyTorch). Deploy it. Compare serving characteristics to sklearn.
- 🛠️ Convert your model to **ONNX** format and serve with ONNX Runtime. Measure performance difference.
- 🔗 Different workload profile than sklearn models — affects your resource planning and HPA strategy.
- 📚 [PyTorch tutorials](https://pytorch.org/tutorials/) · [ONNX Runtime](https://onnxruntime.ai/)

### Week 23 — NLP Pipelines & Transformer Models
- 🧠 Tokenization, embeddings, attention mechanism (conceptual, not mathematical)
- 🧠 Pre-trained models: BERT, GPT, T5 — what they do and how they're served
- 🧠 NLP pipeline components: preprocessing → embedding → model → postprocessing
- 🧠 Serving challenges: large model size, variable-length inputs, token-based billing
- 🛠️ Deploy a **HuggingFace** transformer model (e.g., sentiment analysis). Observe the operational differences from your sklearn model.
- 🛠️ Profile: memory footprint, latency distribution, throughput limitations.
- 🔗 Many ML teams now serve language models. Understanding their operational profile makes you effective.
- 📚 [HuggingFace docs](https://huggingface.co/docs) · [Transformers Course](https://huggingface.co/learn/nlp-course)

### Week 24 — Hyperparameter Tuning & AutoML
- 🧠 What hyperparameter tuning is: automated search for best model configuration
- 🧠 Search strategies: grid, random, Bayesian optimization, early stopping
- 🧠 Compute implications: tuning can run 100+ training jobs — resource scheduling matters
- 🧠 Tools: Optuna, Ray Tune, SageMaker Automatic Model Tuning
- 🧠 AutoML: fully automated model selection and tuning (Google AutoML, H2O)
- 🛠️ Use **Optuna** to tune hyperparameters of your fraud model. Log all trials to MLflow.
- 🛠️ Calculate the compute cost of a tuning run. Design a resource budget policy for tuning.
- 🔗 Tuning jobs are expensive batch workloads. You'll manage scheduling, resource allocation, and cost caps.
- 📚 [Optuna docs](https://optuna.readthedocs.io/) · [Ray Tune](https://docs.ray.io/en/latest/tune/)

### Week 25 — AI Ethics, Bias Mitigation & Regulation
- 🧠 Sources of bias: historical data, sampling, measurement, aggregation, representation
- 🧠 Fairness metrics: demographic parity, equalized odds, calibration across groups
- 🧠 Debiasing techniques: pre-processing (resampling), in-processing (constrained training), post-processing (threshold adjustment)
- 🧠 Regulatory landscape: EU AI Act, NIST AI RMF, SR 11-7, GDPR Article 22
- 🧠 Model risk management frameworks (banking-specific)
- 🛠️ Use **Fairlearn** to assess bias in your fraud model across simulated demographic groups.
- 🛠️ Apply debiasing techniques and measure the accuracy-fairness trade-off.
- 🛠️ Write a "Model Risk Assessment" document using your bank's format.
- 🔗 Compliance is your superpower. Now extend it with specific AI regulation knowledge.
- 📚 [Fairlearn docs](https://fairlearn.org/) · [EU AI Act summary](https://artificialintelligenceact.eu/) · [NIST AI RMF](https://www.nist.gov/artificial-intelligence/ai-risk-management-framework)

### Week 26 — Synthetic Data & Advanced Testing
- 🧠 Why synthetic data: privacy preservation, augmentation, testing, edge case generation
- 🧠 Generation methods: statistical sampling, GANs, rule-based, LLM-generated
- 🧠 ML testing strategies: unit tests for models, property-based testing, metamorphic testing
- 🧠 Contract testing for feature schemas (consumer-driven contracts between teams)
- 🧠 Integration testing for ML pipelines end-to-end
- 🛠️ Generate **synthetic test data** for your model service. Use it to test edge cases and boundary conditions.
- 🛠️ Write a **contract test** for your feature schema: if upstream changes the schema, your test fails before the model breaks.
- 🛠️ Implement **metamorphic tests**: "if I double the transaction amount, the fraud score should increase"
- 🔗 You already write integration tests for services. Apply the same discipline to ML systems, which are notoriously under-tested.
- 📚 [Great Expectations (data contracts)](https://docs.greatexpectations.io/) · [Synthetic Data Vault](https://sdv.dev/)

### Week 27 — ML Team Topologies & Stakeholder Communication
- 🧠 ML team structures: embedded (ML in product teams), platform (central ML infra), hybrid
- 🧠 Roles: ML Engineer vs Data Scientist vs MLOps Engineer vs ML Platform Engineer
- 🧠 On-call design for ML: who responds to drift vs pipeline vs serving alerts
- 🧠 Scaling on-call: training non-ML engineers to handle ML alerts using runbooks
- 🧠 Stakeholder communication: translating model health into business language
- 🧠 Reporting: model health dashboards for leadership, executive summaries
- 🛠️ Design an **on-call rotation** for a team of 6 supporting 10 models across 3 timezones.
- 🛠️ Write a **monthly model health report** template for non-technical leadership.
- 🛠️ Create a **"model health for executives"** dashboard with 3 KPIs per model.
- 🔗 This is pure leadership. You design the team, the processes, and the communication layer.
- 📚 [Team Topologies (book)](https://teamtopologies.com/) · [SRE Workbook — On-Call](https://sre.google/workbook/on-call/)

**Milestone 6:** You can architect ML platforms, communicate across technical/business boundaries, and design teams.

---

## PHASE 8 — SPECIALIZATION TRACKS (Pick Based on Role)

These are deeper dives you pursue based on where your career goes.

### Track A — Feature Pipeline Engineering
- 🧠 Stream processing for features: Apache Kafka + Flink for real-time features
- 🧠 Batch feature computation: Apache Spark, dbt
- 🧠 Hybrid architectures: Lambda/Kappa for combining batch + streaming
- 🛠️ Build a streaming feature pipeline with **Kafka + Python** that computes transaction velocity in real-time and feeds your model.
- 📚 [Kafka docs](https://kafka.apache.org/) · [dbt for ML features](https://docs.getdbt.com/)

### Track B — GitOps for ML
- 🧠 Declarative model deployment with ArgoCD/Flux
- 🧠 Pull-based model promotion through environments
- 🧠 Infrastructure-as-code for ML platforms (Terraform + k8s)
- 🛠️ Set up **ArgoCD** to declaratively manage your model deployment. Push a new model version via git → watch it deploy.
- 📚 [ArgoCD docs](https://argo-cd.readthedocs.io/) · [GitOps for ML (MLOps Community)](https://mlops.community/)

### Track C — Data Governance & Compliance Platform
- 🧠 Enterprise data catalog: Apache Atlas, Amundsen, DataHub
- 🧠 PII detection and masking in training data
- 🧠 Consent management for ML training data
- 🧠 Building a model governance platform (self-service model cards, automated compliance checks)
- 🛠️ Set up **DataHub** locally. Catalog your training datasets and model artifacts with metadata.
- 📚 [DataHub docs](https://datahubproject.io/) · [Privacera](https://privacera.com/)

### Track D — ML Security
- 🧠 Adversarial attacks on models: evasion, poisoning, model extraction
- 🧠 Prompt injection for LLMs
- 🧠 Model supply chain security: signing artifacts, SBOM for ML
- 🧠 Inference-time attack detection
- 🛠️ Run an adversarial attack against your model (e.g., perturbed inputs that flip predictions). Build a detector.
- 📚 [OWASP ML Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/) · [Adversarial Robustness Toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox)

---

## Tooling summary (what you'll touch)

| Category | Tool(s) | Why | Phase |
|---|---|---|---|
| ML basics | scikit-learn, pandas, Jupyter | Feel the workflow | 1 |
| Data validation | Great Expectations / Evidently | Future data-quality alerting | 1 |
| Drift monitoring | Evidently AI (free), Arize/WhyLabs | Core support-lead skill | 1, 3 |
| Experiment tracking / registry | MLflow | Versioning + rollback | 2 |
| Serving | FastAPI + Docker | Wrap models as services | 2 |
| Orchestration | Prefect / ZenML / Kubeflow | Pipelines + retraining | 2 |
| Serving on k8s | KServe / Seldon Core | Your k8s strength | 2 |
| Observability | Prometheus + Grafana | Your SLO strength + ML layer | 3 |
| Data labeling | Label Studio / Prodigy | CloudFactory's domain | 5 |
| Feature stores | Feast / Tecton | Eliminate training-serving skew | 5 |
| LLM/GenAI | LangChain / LlamaIndex / ChromaDB | LLMOps — fastest-growing area | 5 |
| Chaos testing | Custom scripts + Litmus | Validate monitoring under failure | 5 |
| Cloud ML | SageMaker / Vertex AI / Azure ML | Managed platform fluency | 6 |
| Explainability | SHAP / LIME | Regulatory requirement in banking | 6 |
| GPU management | NVIDIA Operator / MIG | Deep learning infrastructure | 6 |
| A/B testing | Seldon / custom router | Multi-model experimentation | 6 |
| Data versioning | DVC / LakeFS / Delta Lake | Reproducibility at scale | 6 |
| Deep learning | PyTorch / ONNX Runtime | Different workload profile | 7 |
| NLP | HuggingFace Transformers | Serve language models | 7 |
| Tuning | Optuna / Ray Tune | Automated model optimization | 7 |
| Fairness | Fairlearn / AIF360 | Bias detection and mitigation | 7 |
| Synthetic data | SDV / Great Expectations | Testing and privacy | 7 |
| Streaming | Kafka / Flink | Real-time features | 8 |
| GitOps for ML | ArgoCD / Flux | Declarative model deployment | 8 |
| Data catalog | DataHub / Amundsen | Enterprise data governance | 8 |
| ML security | ART / OWASP ML Top 10 | Adversarial robustness | 8 |

---

## Recommended structured resources (optional, pick one)

- 📚 **Coursera — "Machine Learning Engineering for Production (MLOps)" specialization** (DeepLearning.AI, Andrew Ng) — the most respected structured course; ops-leaning.
- 📚 **"Designing Machine Learning Systems" by Chip Huyen** (book) — the best single book for system/ops thinking. Read this even if you do nothing else.
- 📚 **"Machine Learning in Production" / Made With ML by Goku Mohandas** (free, online) — hands-on, code-first.
- 📚 **Evidently AI blog & docs** — practical drift/monitoring depth.
- 📚 **Google Cloud / AWS MLOps whitepapers** — for maturity models and reference architectures.

---

## Certifications (optional, for CV signaling)

**Cloud ML Certifications:**
- AWS Certified Machine Learning – Specialty (if your stack is AWS)
- Google Professional Machine Learning Engineer
- Azure AI Engineer Associate

**Platform & DevOps (you may already have these):**
- CKA (Certified Kubernetes Administrator) — validates your k8s depth
- AWS Solutions Architect — validates cloud architecture breadth

**AI Ethics & Governance:**
- AI Ethics Certificate (various providers — good for regulated environments)

**Priority:** Capstone > Phase 5 hands-on work > Certifications. Certs signal; projects prove.

---

## Progress tracker

- [ ] Phase 0 — Orientation
- [ ] Phase 1 — ML Foundations (Weeks 1–3) + Milestone 1
- [ ] Phase 2 — MLOps Platform (Weeks 4–7) + Milestone 2
- [ ] Phase 3 — Monitoring & Governance (Weeks 8–10) + Milestone 3
- [ ] Phase 4 — Capstone (Weeks 11–12)
- [ ] Phase 5 — High Priority Extensions (Weeks 13–16) + Milestone 4
- [ ] Phase 6 — Medium Priority (Weeks 17–21) + Milestone 5
- [ ] Phase 7 — Advanced Topics (Weeks 22–27) + Milestone 6
- [ ] Phase 8 — Specialization Tracks (pick based on role direction)

---

## A note on sequencing for your interview

You don't need to finish this course before the call. For the **introductory call next week**,
Phase 0 + Week 3 concepts (the drift family) are enough to sound informed.
The full course is for genuinely *becoming* strong in MLOps over the next 3 months.

**Phases 1–4 (Weeks 1–12):** Core competency. Complete this in 12 weeks to be job-ready.  
**Phase 5 (Weeks 13–16):** Do these in your first month on the job. Directly relevant to CloudFactory.  
**Phase 6 (Weeks 17–21):** Do these in months 2–3. Deepens your platform leadership.  
**Phase 7 (Weeks 22–27):** Long-term growth. Pick based on what the team needs.  
**Phase 8:** Career specialization. Choose a track based on where you want to grow.

**Total curriculum:** ~27 weeks (6–7 months) for comprehensive MLOps expertise, from operational fluency to strategic architecture.
