"""
Model Training Script
=====================
Trains a simple Iris classifier and saves it as a .pkl file.

This simulates what a data scientist would hand off to you:
- A trained model artifact (model.pkl)
- Metadata about the model (model_metadata.json)

In production, this would be handled by an ML pipeline (Airflow, Kubeflow, etc.)
and the artifact would be stored in a model registry. For now, we just save to disk.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = Path(__file__).parent / "model_artifacts"
MODEL_PATH = MODEL_DIR / "model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def train_and_save_model():
    """Train an Iris classifier and save the model + metadata."""

    logger.info("Loading Iris dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target
    feature_names = iris.feature_names
    target_names = list(iris.target_names)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"Training set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")

    # Train model
    logger.info("Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Model accuracy: {accuracy:.4f}")
    logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=target_names)}")

    # Save model artifact
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Model saved to: {MODEL_PATH}")

    # Save metadata (this is what your /model-info endpoint will serve)
    metadata = {
        "model_name": "iris-classifier",
        "model_version": "1.0.0",
        "algorithm": "RandomForestClassifier",
        "framework": "scikit-learn",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "accuracy": float(accuracy),
        "feature_names": feature_names,
        "target_names": target_names,
        "n_features": len(feature_names),
        "n_classes": len(target_names),
        "training_samples": int(X_train.shape[0]),
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 5,
            "random_state": 42,
        },
        "feature_ranges": {
            name: {"min": float(np.min(X[:, i])), "max": float(np.max(X[:, i]))}
            for i, name in enumerate(feature_names)
        },
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata saved to: {METADATA_PATH}")

    logger.info("\n✅ Model training complete. You can now start the API server:")
    logger.info("   uvicorn app.main:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    train_and_save_model()
