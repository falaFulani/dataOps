"""
ML Observability Metrics — Week 8
==================================
Custom Prometheus metrics for a model serving endpoint.

This module instruments a model service with TWO layers of metrics:

Layer 1 (Operational) — You already know these patterns:
  - Request count, latency histogram, error tracking
  - Same as any microservice you instrument today

Layer 2 (ML-Specific) — The new layer you're adding:
  - Prediction confidence distribution
  - Model drift score
  - Data quality rate
  - Per-feature drift detection

All metrics are exposed at /metrics in Prometheus format.
Prometheus scrapes them. Grafana visualizes them. Same stack, new signals.

Usage:
    from app.metrics import track_prediction, update_drift_scores

    # On each prediction:
    track_prediction(
        model_version="1.0.0",
        predicted_class="setosa",
        confidence=0.97,
        latency_seconds=0.012,
    )

    # On a schedule (e.g., every 5 minutes via background task):
    update_drift_scores(
        overall_drift=0.15,
        feature_drifts={"sepal_length": 0.0, "sepal_width": 0.1, ...},
    )
"""

from prometheus_client import Counter, Gauge, Histogram, Info

# =============================================================================
# LAYER 1: OPERATIONAL METRICS
# =============================================================================
# These are the standard metrics you'd add to any service.
# Nothing ML-specific here — this is your comfort zone.

# ---------------------------------------------------------------------------
# prediction_requests_total
# ---------------------------------------------------------------------------
# Counter: Total number of predictions served.
#
# Labels:
#   - model_version: Which model version generated this prediction.
#     Lets you compare traffic between canary/stable during rollouts.
#   - predicted_class: What the model predicted.
#     Track distribution of outputs — if this shifts, something changed.
#
# Why it matters:
#   - Traffic volume (SLI for throughput)
#   - Prediction distribution (ML signal — shift = possible drift)
#   - Per-version breakdown (canary analysis)
prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total number of prediction requests served",
    labelnames=["model_version", "predicted_class"],
)

# ---------------------------------------------------------------------------
# prediction_latency_seconds
# ---------------------------------------------------------------------------
# Histogram: How long each prediction takes (inference time only).
#
# Buckets are tuned for ML inference workloads:
#   - Simple models (sklearn): 1ms - 50ms
#   - Medium models (XGBoost, small neural nets): 50ms - 200ms
#   - Large models (transformers): 200ms - 5000ms
#
# Why it matters:
#   - SLI for your latency SLO (e.g., p99 < 200ms)
#   - Detects model performance degradation
#   - Distinguishes model latency from network/framework overhead
prediction_latency_seconds = Histogram(
    "prediction_latency_seconds",
    "Time spent computing the prediction (model inference only)",
    buckets=[
        0.001, 0.005, 0.01, 0.025, 0.05, 0.075,
        0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0,
    ],
)


# =============================================================================
# LAYER 2: ML-SPECIFIC METRICS
# =============================================================================
# These are the NEW metrics that traditional monitoring doesn't have.
# They catch the "green pipeline, wrong predictions" failure mode.

# ---------------------------------------------------------------------------
# prediction_confidence
# ---------------------------------------------------------------------------
# Histogram: Distribution of model confidence scores (probability of
# the predicted class).
#
# Buckets from 0 to 1 in 0.1 increments, with extra granularity at the
# high end where most production predictions should cluster.
#
# Why it matters:
#   - LEADING INDICATOR of model degradation
#   - If confidence drops (p50 goes from 0.95 to 0.75), the model is
#     becoming uncertain — likely seeing data it wasn't trained on
#   - You can alert on this BEFORE accuracy actually drops
#   - Think of it like: "the model is less sure of itself" = early warning
#
# Alert idea: p50(prediction_confidence) < 0.8 for 15 minutes
prediction_confidence = Histogram(
    "prediction_confidence",
    "Confidence score (predicted class probability) distribution",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99, 1.0],
)

# ---------------------------------------------------------------------------
# model_drift_score
# ---------------------------------------------------------------------------
# Gauge: Overall drift score from statistical tests comparing current
# input data distribution to the training data distribution.
#
# Value range: 0.0 (no drift) to 1.0 (complete distribution shift)
# Typically computed using Population Stability Index (PSI) or
# Kolmogorov-Smirnov test across all features, then normalized.
#
# Why it matters:
#   - Single number that says "how different is current data from training data?"
#   - This is your SLI for data relevance
#   - High drift score = model's training assumptions no longer hold
#   - Does NOT mean the model is wrong yet — but it's at risk
#
# Thresholds (common starting points):
#   - < 0.1: No significant drift (green)
#   - 0.1 - 0.25: Minor drift, monitor (yellow)
#   - 0.25 - 0.5: Moderate drift, investigate (orange)
#   - > 0.5: Major drift, consider retraining (red)
#
# Updated by a background job, not on every request (too expensive).
model_drift_score = Gauge(
    "model_drift_score",
    "Overall model drift score (0=no drift, 1=full drift). "
    "Computed from statistical tests on input feature distributions.",
)

# ---------------------------------------------------------------------------
# data_quality_score
# ---------------------------------------------------------------------------
# Gauge: Percentage of incoming prediction requests that pass all
# data quality checks (valid schema, no missing values, values in range).
#
# Value range: 0.0 (all requests invalid) to 1.0 (all requests valid)
#
# Why it matters:
#   - Bad inputs → bad predictions, silently
#   - If upstream data pipelines break, this is your first signal
#   - A model can be perfectly trained but produce garbage if fed garbage
#   - This catches feature pipeline failures before they reach the model
#
# Alert idea: data_quality_score < 0.95 for 5 minutes
data_quality_score = Gauge(
    "data_quality_score",
    "Fraction of prediction requests passing all data quality checks (0-1). "
    "Drops indicate upstream data pipeline issues.",
)

# ---------------------------------------------------------------------------
# feature_drift_detected
# ---------------------------------------------------------------------------
# Gauge (per feature): Binary indicator of whether each individual feature
# has drifted beyond its threshold.
#
# Labels:
#   - feature_name: Name of the feature (e.g., "sepal_length", "credit_score")
#
# Value: 0 (no drift) or 1 (drift detected)
#
# Why it matters:
#   - model_drift_score tells you THAT drift happened
#   - feature_drift_detected tells you WHERE it happened
#   - If "credit_score" drifts but other features are stable, you know
#     exactly which upstream pipeline to investigate
#   - This is the "which component is broken?" signal
#
# In practice: computed by running a KS test or PSI on each feature
# against its reference distribution from training data.
feature_drift_detected = Gauge(
    "feature_drift_detected",
    "Per-feature drift indicator (0=stable, 1=drift detected)",
    labelnames=["feature_name"],
)

# ---------------------------------------------------------------------------
# Additional ML Context Metrics (informational)
# ---------------------------------------------------------------------------

# How old the training data is — freshness matters
data_freshness_seconds = Gauge(
    "data_freshness_seconds",
    "Age of the most recent data used to train the current model (seconds). "
    "Stale data = stale model assumptions.",
)

# When the model was last trained (unix timestamp)
model_last_trained_timestamp = Gauge(
    "model_last_trained_timestamp",
    "Unix timestamp of when the current model was last trained. "
    "Use to compute model age: time() - model_last_trained_timestamp.",
)

# Model info (static labels — useful for filtering/grouping)
model_info = Info(
    "model",
    "Static information about the currently loaded model",
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
# These wrap the raw metrics and provide a clean API for the model service
# to call on each prediction and on scheduled background updates.


def track_prediction(
    model_version: str,
    predicted_class: str,
    confidence: float,
    latency_seconds: float,
) -> None:
    """Record metrics for a single prediction.

    Call this on EVERY prediction request. It's cheap — just counter/histogram
    increments, no computation.

    Args:
        model_version: Version of the model that made this prediction
        predicted_class: The class/label the model predicted
        confidence: Probability of the predicted class (0-1)
        latency_seconds: Time taken for model inference (seconds)
    """
    # Layer 1: Operational
    prediction_requests_total.labels(
        model_version=model_version,
        predicted_class=predicted_class,
    ).inc()
    prediction_latency_seconds.observe(latency_seconds)

    # Layer 2: ML-specific
    prediction_confidence.observe(confidence)


def update_drift_scores(
    overall_drift: float,
    feature_drifts: dict[str, float],
    drift_threshold: float = 0.5,
) -> None:
    """Update drift metrics from a background drift computation job.

    Call this on a SCHEDULE (e.g., every 5 minutes), not on every request.
    Drift computation requires comparing current data to reference data,
    which is too expensive to run per-request.

    Args:
        overall_drift: Normalized drift score across all features (0-1)
        feature_drifts: Per-feature drift scores {feature_name: score}
        drift_threshold: Score above which a feature is considered drifted
    """
    model_drift_score.set(overall_drift)

    for feature_name, drift_value in feature_drifts.items():
        # Set binary indicator: 1 if drift exceeds threshold, 0 otherwise
        feature_drift_detected.labels(feature_name=feature_name).set(
            1.0 if drift_value > drift_threshold else 0.0
        )


def update_data_quality(quality_rate: float) -> None:
    """Update the data quality score.

    Call this after validating incoming requests. Can be computed as a
    rolling average or per-batch.

    Args:
        quality_rate: Fraction of requests passing quality checks (0-1)
    """
    data_quality_score.set(quality_rate)


def set_model_info(
    model_name: str,
    model_version: str,
    trained_at_timestamp: float,
    algorithm: str = "unknown",
) -> None:
    """Set static model information metrics. Call once at startup.

    Args:
        model_name: Name of the model
        model_version: Version string
        trained_at_timestamp: Unix timestamp when model was trained
        algorithm: Algorithm/framework used
    """
    model_info.info({
        "name": model_name,
        "version": model_version,
        "algorithm": algorithm,
    })
    model_last_trained_timestamp.set(trained_at_timestamp)


def update_data_freshness(freshness_seconds: float) -> None:
    """Update data freshness gauge.

    Args:
        freshness_seconds: Age of the newest data point in the training set
    """
    data_freshness_seconds.set(freshness_seconds)


# =============================================================================
# EXAMPLE: How This Integrates With Your FastAPI Service
# =============================================================================
#
# In your main.py (or wherever your /predict endpoint lives):
#
#   import time
#   from app.metrics import track_prediction, update_data_quality
#
#   @app.post("/predict")
#   def predict(request: PredictionRequest):
#       start = time.perf_counter()
#
#       # ... run inference ...
#       prediction = model.predict(features)
#       confidence = model.predict_proba(features).max()
#
#       latency = time.perf_counter() - start
#
#       # Track the prediction (both layers in one call)
#       track_prediction(
#           model_version="1.0.0",
#           predicted_class=prediction,
#           confidence=confidence,
#           latency_seconds=latency,
#       )
#
#       return {"prediction": prediction, "confidence": confidence}
#
#
# In a background task (or sidecar container running Evidently):
#
#   from app.metrics import update_drift_scores, update_data_freshness
#
#   @scheduler.every(minutes=5)
#   def compute_drift():
#       # Compare current request data to training reference
#       drift_report = evidently.calculate(current_data, reference_data)
#
#       update_drift_scores(
#           overall_drift=drift_report.overall_score,
#           feature_drifts=drift_report.per_feature_scores,
#       )
#       update_data_freshness(
#           freshness_seconds=time.time() - training_data_timestamp
#       )
