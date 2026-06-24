# Week 1 — How ML Actually Works (Just Enough)

**Time budget:** 6–8 hours  
**Goal:** Understand the ML lifecycle end-to-end and feel the workflow hands-on.  
You are NOT becoming a data scientist — you're learning what the team operates.

---

## Concepts to cover

### 1. Supervised vs Unsupervised Learning

| Type | What it does | Example |
|------|-------------|---------|
| **Supervised** | Learns from labeled data (inputs + correct answers) | Predict fraud (yes/no) from transaction features |
| **Unsupervised** | Finds patterns in unlabeled data | Cluster customers into segments |

Most production ML you'll support is **supervised** — classification or regression.

### 2. Training vs Inference

- **Training:** Feed data + labels into an algorithm → produces a model (a file with learned patterns)
- **Inference:** Feed new data into the trained model → get predictions

Think of it like: training = building the binary, inference = running the binary in prod.

### 3. What's a "Model" and a "Feature"?

- **Model:** A mathematical function learned from data. In practice, it's a serialized file (`.pkl`, `.onnx`, `.pt`) that takes input and returns a prediction.
- **Feature:** A measurable property used as input. Example: for fraud detection, features might be `transaction_amount`, `time_since_last_transaction`, `merchant_category`.
- **Feature engineering:** Transforming raw data into useful features the model can learn from.

### 4. The ML Lifecycle

```
Data Collection → Data Validation → Feature Engineering → Training → Evaluation → Deployment → Monitoring → Retraining
                                                                                                      ↑                    |
                                                                                                      └────────────────────┘
```

Compare to your software release cycle:
- Code → Build → Test → Deploy → Monitor → Patch
- Data → Train → Evaluate → Deploy → Monitor → Retrain

### 5. Why ML Fails Silently (The Core Operator Insight)

Traditional software: bug → exception → alert → you fix it.  
ML system: model degrades → predictions get worse → **no error is thrown** → users/business hurt silently.

**This is the single most important insight for your role.** It's why ML monitoring
is a separate discipline from infrastructure monitoring. The pipeline is green,
the pods are healthy, latency is fine — but the model is confidently wrong.

---

## Hands-on Lab

Open `lab-train-simple-model.ipynb` and work through it.  
You'll train a simple classifier, make predictions, and measure accuracy.  
Don't optimize — just feel the workflow.

---

## Connect to your ops background

| Your current world | ML equivalent |
|---|---|
| Deploy a service | Deploy a model |
| Service version / rollback | Model version / rollback |
| Health check endpoint | Model health + prediction quality |
| Logs & metrics | Predictions logged + drift metrics |
| Incident: service is down | Incident: model accuracy dropped |
| Post-incident review | Post-incident review (same, + drift analysis) |

---

## Resources

- 📚 [Machine Learning for Everybody — freeCodeCamp](https://www.youtube.com/watch?v=i_LwzRVP7bg) (watch at 1.5x, skip math derivations)
- 📚 Andrew Ng's ML intro (Coursera, free to audit) — first 2 weeks only
- 📚 [Google ML Crash Course — Framing](https://developers.google.com/machine-learning/crash-course/framing/video-lecture)

---

## Checklist

- [ ] Read through concepts above
- [ ] Complete the lab notebook
- [ ] Write 3–5 sentences comparing the ML lifecycle to your current release lifecycle
- [ ] Watch at least one resource video/article
