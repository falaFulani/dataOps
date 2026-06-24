# Week 2 — Data Is the Product

**Time budget:** 6–8 hours  
**Goal:** Understand why data quality is the #1 operational concern in production ML,
and learn to validate it the same way you'd validate API contracts.

---

## The core insight

In traditional systems, bugs live in code. In ML systems, **bugs live in data.**

A model is only as good as the data it was trained on — and only stays good if
production data keeps matching what it learned. You can have a perfect model
architecture, flawless deployment, green pods, low latency — and still deliver
confidently wrong predictions because the input data silently shifted.

**Your job as an ML support lead:** Treat data as a first-class operational concern.
Data pipelines need the same rigor you give to service deploys — contracts, validation,
monitoring, and alerting.

---

## Concepts to cover

### 1. Data quality matters more than model quality

Data scientists spend weeks tuning model hyperparameters to gain 0.5% accuracy.
Meanwhile, a single upstream schema change can drop accuracy by 20% overnight.

In practice:
- **80% of ML system failures** trace back to data issues, not model issues
- A mediocre model on clean data beats a great model on dirty data
- Most "model degradation" incidents are actually data incidents

**Operator takeaway:** Invest in data validation before model monitoring. It's cheaper
and catches problems earlier.

### 2. Schema validation

**What it is:** A set of rules that define what "correct" data looks like — column names,
data types, value ranges, non-null constraints, expected distributions.

**Why it matters:** Silent schema changes are the #1 cause of ML pipeline failures.
An upstream team adds a column, renames a field, or changes an enum from strings to ints.
No exception is thrown. The model receives garbage and produces garbage predictions.

Schema validation catches this at the gate — the same way API contract testing catches
breaking changes in microservices.

Examples of schema rules:
- Column `transaction_amount` must exist, be a float, and be between 0 and 1,000,000
- Column `merchant_category` must be one of 15 known enum values
- No nulls in `customer_id`
- DataFrame must have exactly 12 columns

### 3. Feature engineering basics

**What it is:** Transforming raw data into inputs the model can actually learn from.

Raw data is messy. Models expect clean numerical inputs. Feature engineering bridges that gap:

| Raw data | Engineered feature | Why |
|----------|-------------------|-----|
| Timestamp `2024-01-15 14:30:00` | `hour_of_day = 14`, `is_weekend = 0` | Model can't read timestamps directly |
| Merchant name "AMAZON.COM" | `merchant_category = "online_retail"` | Reduces cardinality, adds meaning |
| Transaction amounts [5, 500, 50000] | `log_amount = log(amount)` | Normalizes the scale |
| Country "Kenya" | One-hot: `country_KE = 1, country_UG = 0, ...` | Converts categories to numbers |

**Operator takeaway:** Feature engineering code is part of your production pipeline.
If training uses one set of transformations and serving uses a different set, predictions
will be wrong. This leads us to the next concept...

### 4. Train/test splits — why they matter

- **Training set:** What the model learns patterns from (~80% of data)
- **Test set:** Held-back data the model never sees during training (~20%)
- **Purpose:** The test set simulates production. If the model performs well on test data,
  it should perform well on similar real-world data.

**Why this matters to operators:**
- If someone accidentally includes test data in training ("data leakage"), the model
  looks perfect in evaluation but fails in production
- This is like running tests that always pass because they're testing themselves
- In production monitoring, your baseline metrics should come from test set performance

### 5. Training-serving skew — THE critical failure mode

**Definition:** When data processing in production doesn't exactly match data processing
during training.

This is subtle, insidious, and causes more production incidents than almost anything else.

**Example:**
```
Training code:  amount_normalized = (amount - mean) / std    # mean=500, std=200
Serving code:   amount_normalized = amount / 1000             # "close enough" shortcut
```

The model learned patterns based on the first normalization. When serving uses different
normalization, every single prediction is off — but no error is thrown.

**Common causes:**
- Different code paths for training vs serving (Python training, Java serving)
- Feature engineering done in a notebook, then reimplemented differently for prod
- Different library versions (pandas 1.x vs 2.x handle NaN differently)
- Data joins done in different order (SQL vs Python)
- Timezone handling differences

**Operator takeaway:** This is why ML teams push for "one pipeline, two modes" —
the exact same feature transformation code runs in both training and serving.
Any divergence is a bug. Treat it like a config drift between staging and production.

---

## Connect to your ops background

| ML concept | Your ops equivalent | Why the mapping helps |
|---|---|---|
| Schema validation | API contract testing / OpenAPI spec | Both catch breaking interface changes at the boundary |
| Data quality checks | Health checks + input validation | Both verify "is what I'm receiving actually correct?" |
| Feature engineering pipeline | Build pipeline / CI transforms | Both transform raw inputs into a usable artifact |
| Train/test split | Staging vs production traffic | Both simulate prod to catch issues before real users are affected |
| Training-serving skew | Config drift between environments | Both cause silent failures because the system "works" but produces wrong results |
| Data quality SLO | Service availability SLO | Both define "what does acceptable look like?" with measurable thresholds |
| Great Expectations suite | Integration test suite | Both encode "what correct looks like" as executable assertions |
| Data pipeline monitoring | Pipeline/CI health dashboard | Both need alerting when upstream changes break downstream consumers |

---

## Hands-on Lab

Open `lab-data-validation.ipynb` and work through it.

You'll:
1. Write data validation rules using pandas (Great Expectations style)
2. Introduce data quality issues and watch what happens to model predictions
3. Create a training-serving skew scenario and see it fail silently
4. Build a validation summary that maps directly to future alerts

---

## Resources

- 📚 [Google's Data Validation in ML](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) — Sections on data validation in production
- 📚 [Great Expectations Documentation](https://docs.greatexpectations.io/docs/) — The standard open-source data validation library
- 📚 ["Everyone wants to do the model work, not the data work" (Google Research paper)](https://research.google/pubs/pub49953/) — Why data quality is the real bottleneck
- 📚 [Training-Serving Skew — Google ML Best Practices](https://developers.google.com/machine-learning/guides/rules-of-ml#training-serving_skew) — Rules 32-36 in Google's Rules of ML
- 📚 [Chip Huyen — "Designing ML Systems" Chapter 4](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/) — Feature engineering and data issues in production

---

## Checklist

- [ ] Read through concepts above (focus on training-serving skew — you'll be asked about it)
- [ ] Run `setup.sh` to create the Week 2 environment
- [ ] Complete the lab notebook end-to-end
- [ ] Write 3–5 sentences: "How would I detect training-serving skew in a production system I operate?"
- [ ] Draft 2–3 data quality SLOs you'd define for a fraud detection model (e.g., "null rate in `amount` column < 0.1%")
- [ ] Review at least one resource link above
