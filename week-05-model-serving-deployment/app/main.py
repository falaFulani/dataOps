"""
Model Serving API
=================
A FastAPI application that serves predictions from a trained ML model.

This is the same pattern as any API you'd deploy:
- Load business logic (in this case, a model file instead of application code)
- Expose endpoints
- Validate input
- Return structured responses
- Log everything for observability

The only "ML-specific" parts:
- Loading a .pkl file instead of connecting to a database
- Returning confidence scores alongside predictions
- Tracking prediction distribution for monitoring
"""

import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_DIR = Path(__file__).parent / "model_artifacts"
MODEL_PATH = MODEL_DIR / "model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("model-service")

# ---------------------------------------------------------------------------
# Global State (loaded at startup)
# ---------------------------------------------------------------------------

model = None
model_metadata = None
model_loaded_at = None

# ---------------------------------------------------------------------------
# Pydantic Models (Input Validation & Output Schema)
# ---------------------------------------------------------------------------


class PredictionRequest(BaseModel):
    """Input schema for the prediction endpoint.

    For the Iris model, expects 4 numerical features:
    - sepal_length (cm)
    - sepal_width (cm)
    - petal_length (cm)
    - petal_width (cm)
    """

    features: list[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="List of 4 numerical features: [sepal_length, sepal_width, petal_length, petal_width]",
        examples=[[5.1, 3.5, 1.4, 0.2]],
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, v):
        """Ensure all features are finite numbers."""
        for i, val in enumerate(v):
            if not np.isfinite(val):
                raise ValueError(f"Feature at index {i} must be a finite number, got {val}")
            if val < 0:
                raise ValueError(f"Feature at index {i} must be non-negative, got {val}")
        return v


class PredictionResponse(BaseModel):
    """Output schema for predictions."""

    prediction_id: str = Field(..., description="Unique ID for this prediction (audit trail)")
    prediction: str = Field(..., description="Predicted class label")
    confidence: float = Field(..., description="Confidence score (probability of predicted class)")
    probabilities: dict[str, float] = Field(..., description="Probability for each class")
    model_version: str = Field(..., description="Version of the model used")
    timestamp: str = Field(..., description="ISO timestamp of prediction")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str


class ModelInfoResponse(BaseModel):
    """Model information response."""

    model_name: str
    model_version: str
    algorithm: str
    framework: str
    trained_at: str
    loaded_at: str
    accuracy: float
    feature_names: list[str]
    target_names: list[str]
    n_features: int
    n_classes: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: Optional[str] = None
    timestamp: str


# ---------------------------------------------------------------------------
# Application Lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    global model, model_metadata, model_loaded_at

    logger.info("Starting model service...")

    # Load model
    if not MODEL_PATH.exists():
        logger.error(f"Model file not found: {MODEL_PATH}")
        logger.error("Run 'python app/model_training.py' first to train and save a model.")
        # Don't crash — let readiness check handle this gracefully
        model = None
        model_metadata = None
    else:
        try:
            model = joblib.load(MODEL_PATH)
            model_loaded_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"Model loaded from: {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            model = None

    # Load metadata
    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH) as f:
                model_metadata = json.load(f)
            logger.info(f"Model metadata loaded: {model_metadata.get('model_name')} v{model_metadata.get('model_version')}")
        except Exception as e:
            logger.error(f"Failed to load model metadata: {e}")
            model_metadata = {}
    else:
        model_metadata = {}

    logger.info("Model service ready to accept requests.")
    yield

    # Shutdown
    logger.info("Shutting down model service...")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ML Model Serving API",
    description=(
        "A production-ready model serving endpoint. "
        "Same as any API service you deploy — the business logic just happens to be a model file."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
def health_check():
    """Liveness probe — is the service process running?

    This is your standard liveness check. If this fails, Kubernetes
    should restart the pod. Same as any other service.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/ready", tags=["Operations"])
def readiness_check():
    """Readiness probe — can the service serve predictions?

    Unlike liveness, this checks if the model is actually loaded and ready.
    If this fails, Kubernetes should stop routing traffic to this pod
    (but NOT restart it — the model might still be loading).
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service is not ready to serve predictions.",
        )
    return {
        "status": "ready",
        "model_loaded": True,
        "model_version": model_metadata.get("model_version", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Operations"])
def get_model_info():
    """Returns information about the currently loaded model.

    Useful for debugging, audit, and confirming which model version
    is serving in each environment (same as checking a /version endpoint).
    """
    if model is None or not model_metadata:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run model_training.py first.",
        )

    return ModelInfoResponse(
        model_name=model_metadata.get("model_name", "unknown"),
        model_version=model_metadata.get("model_version", "unknown"),
        algorithm=model_metadata.get("algorithm", "unknown"),
        framework=model_metadata.get("framework", "unknown"),
        trained_at=model_metadata.get("trained_at", "unknown"),
        loaded_at=model_loaded_at or "unknown",
        accuracy=model_metadata.get("accuracy", 0.0),
        feature_names=model_metadata.get("feature_names", []),
        target_names=model_metadata.get("target_names", []),
        n_features=model_metadata.get("n_features", 0),
        n_classes=model_metadata.get("n_classes", 0),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
def predict(request: PredictionRequest):
    """Generate a prediction from the model.

    Accepts feature values, runs inference, returns prediction with confidence.

    This is the core endpoint — equivalent to your service's main business logic
    endpoint, except the logic is 'load features into model, get prediction out.'
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service is not ready.",
        )

    # Generate prediction ID for audit trail
    prediction_id = str(uuid.uuid4())

    try:
        # Reshape input for sklearn (expects 2D array)
        features_array = np.array(request.features).reshape(1, -1)

        # Get prediction and probabilities
        prediction_idx = model.predict(features_array)[0]
        probabilities = model.predict_proba(features_array)[0]

        # Map to class names
        target_names = model_metadata.get("target_names", [str(i) for i in range(len(probabilities))])
        predicted_class = target_names[prediction_idx]
        confidence = float(probabilities[prediction_idx])

        # Build probability dict
        prob_dict = {name: round(float(prob), 4) for name, prob in zip(target_names, probabilities)}

        timestamp = datetime.now(timezone.utc).isoformat()

        # Log the prediction (for future monitoring — Week 7 will use these logs)
        logger.info(
            f"PREDICTION | id={prediction_id} | input={request.features} | "
            f"prediction={predicted_class} | confidence={confidence:.4f} | "
            f"timestamp={timestamp}"
        )

        return PredictionResponse(
            prediction_id=prediction_id,
            prediction=predicted_class,
            confidence=round(confidence, 4),
            probabilities=prob_dict,
            model_version=model_metadata.get("model_version", "unknown"),
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"Prediction failed | id={prediction_id} | error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Run directly (development only)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
