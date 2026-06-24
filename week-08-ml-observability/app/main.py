"""
Model Service with ML Observability — Week 8
=============================================
FastAPI service that serves predictions AND exposes Prometheus metrics
for both operational and ML-specific monitoring.

This builds on the Week 5 model service. The difference:
- prometheus_client library integrated
- Custom metrics from app/metrics.py recorded on every prediction
- Background task simulates drift score updates (in production, this
  would be a separate job or sidecar running Evidently)
- /metrics endpoint exposed for Prometheus to scrape

Architecture:
  /predict → runs inference → records latency + confidence + class
  /metrics → Prometheus scrapes this for both layers
  Background task → computes drift scores every 30s (simulated)
"""

import asyncio
import logging
import random
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)
from pydantic import BaseModel, Field

from app.metrics import (
    set_model_info,
    track_prediction,
    update_data_freshness,
    update_data_quality,
    update_drift_scores,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH = Path("/app/model.pkl")
MODEL_VERSION = "1.0.0"
MODEL_NAME = "iris-classifier"
FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
TARGET_NAMES = ["setosa", "versicolor", "virginica"]

logger = logging.getLogger("model-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
model = None
quality_tracker = {"total": 0, "valid": 0}


# ---------------------------------------------------------------------------
# Model Training (runs at Docker build time)
# ---------------------------------------------------------------------------
def train_model():
    """Train a simple Iris classifier and save it. Run at build time."""
    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    iris = load_iris()
    X_train, _, y_train, _ = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    logger.info(f"Model trained and saved to {MODEL_PATH}")


# ---------------------------------------------------------------------------
# Background Drift Simulation
# ---------------------------------------------------------------------------
async def drift_computation_loop():
    """Simulates periodic drift computation.

    In production, this would:
    1. Collect recent prediction inputs from a buffer/queue
    2. Run statistical tests (KS, PSI) against training reference data
    3. Update the drift gauges

    Here we simulate with random values so you can see the gauges move
    on the Grafana dashboard. Replace this with real Evidently calls
    when you have a reference dataset.
    """
    while True:
        await asyncio.sleep(30)  # Compute drift every 30 seconds

        # Simulated drift scores (in production: Evidently or manual stats)
        overall_drift = random.uniform(0.05, 0.35)
        feature_drifts = {
            "sepal_length": random.uniform(0.0, 0.4),
            "sepal_width": random.uniform(0.0, 0.3),
            "petal_length": random.uniform(0.0, 0.5),
            "petal_width": random.uniform(0.0, 0.25),
        }

        update_drift_scores(
            overall_drift=overall_drift,
            feature_drifts=feature_drifts,
            drift_threshold=0.3,
        )

        # Simulated data freshness (model trained 3 days ago)
        model_age_seconds = 3 * 24 * 3600 + random.uniform(0, 3600)
        update_data_freshness(model_age_seconds)

        logger.info(
            f"Drift update: overall={overall_drift:.3f}, "
            f"features={', '.join(f'{k}={v:.2f}' for k, v in feature_drifts.items())}"
        )


# ---------------------------------------------------------------------------
# Application Lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and start background tasks on startup."""
    global model

    # Load model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded from {MODEL_PATH}")
    else:
        logger.warning("No model file found. Train with: python -c 'from app.main import train_model; train_model()'")

    # Set static model info metrics
    trained_timestamp = time.time() - (3 * 24 * 3600)  # Pretend trained 3 days ago
    set_model_info(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        trained_at_timestamp=trained_timestamp,
        algorithm="RandomForestClassifier",
    )

    # Initialize drift and quality scores
    update_drift_scores(
        overall_drift=0.1,
        feature_drifts={name: 0.05 for name in FEATURE_NAMES},
    )
    update_data_quality(1.0)

    # Start background drift computation
    drift_task = asyncio.create_task(drift_computation_loop())

    yield

    # Cleanup
    drift_task.cancel()
    logger.info("Model service shutting down.")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ML Model Service (with Observability)",
    description="Week 8 — Model serving with Prometheus metrics for both operational and ML monitoring layers.",
    version=MODEL_VERSION,
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------
class PredictionRequest(BaseModel):
    features: list[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="4 features: [sepal_length, sepal_width, petal_length, petal_width]",
        examples=[[5.1, 3.5, 1.4, 0.2]],
    )


class PredictionResponse(BaseModel):
    prediction_id: str
    prediction: str
    confidence: float
    probabilities: dict[str, float]
    model_version: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness probe — process is running."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready")
def ready():
    """Readiness probe — model is loaded and ready to serve."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model_version": MODEL_VERSION}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint.

    Exposes all custom metrics (both operational and ML-specific) in
    Prometheus exposition format. This is what Prometheus scrapes.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Generate a prediction and record observability metrics.

    On each call, this endpoint:
    1. Validates input (data quality check)
    2. Runs inference
    3. Records operational metrics (latency, request count)
    4. Records ML metrics (confidence, prediction class)
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    prediction_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # --- Data quality check ---
    quality_tracker["total"] += 1
    features_valid = all(np.isfinite(f) and f >= 0 for f in request.features)
    if features_valid:
        quality_tracker["valid"] += 1

    # Update quality score (rolling)
    if quality_tracker["total"] > 0:
        quality_rate = quality_tracker["valid"] / quality_tracker["total"]
        update_data_quality(quality_rate)

    # --- Run inference ---
    features_array = np.array(request.features).reshape(1, -1)
    prediction_idx = model.predict(features_array)[0]
    probabilities = model.predict_proba(features_array)[0]

    predicted_class = TARGET_NAMES[prediction_idx]
    confidence = float(probabilities[prediction_idx])

    # --- Record metrics (both layers in one call) ---
    latency = time.perf_counter() - start_time
    track_prediction(
        model_version=MODEL_VERSION,
        predicted_class=predicted_class,
        confidence=confidence,
        latency_seconds=latency,
    )

    # --- Build response ---
    prob_dict = {name: round(float(p), 4) for name, p in zip(TARGET_NAMES, probabilities)}

    return PredictionResponse(
        prediction_id=prediction_id,
        prediction=predicted_class,
        confidence=round(confidence, 4),
        probabilities=prob_dict,
        model_version=MODEL_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Run directly (development)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
