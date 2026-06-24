"""
Week 6 — ML Pipeline with Prefect
==================================

This pipeline automates the ML workflow: validate → train → evaluate → register.

Think of it as a CI/CD pipeline for models:
    - validate_data   = lint       (catch bad inputs early)
    - train_model     = build      (transform source into artifact)
    - evaluate_model  = test       (gate on quality before promotion)
    - register_model  = deploy     (promote artifact to registry)

Run with:
    python pipeline.py

Requirements:
    pip install prefect scikit-learn pandas pyyaml
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
import yaml
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.model_selection import train_test_split


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def load_config(config_path: str = "pipeline_config.yml") -> dict:
    """Load pipeline configuration from YAML file.

    Same principle as loading Helm values or reading pipeline variables.
    Config lives separately from logic so you can change behavior without
    touching code.
    """
    config_file = Path(__file__).parent / config_path
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


# =============================================================================
# TASK 1: LOAD AND VALIDATE DATA
# =============================================================================
# CI/CD equivalent: LINT
# Purpose: Catch bad data before it propagates downstream.
# If your data is garbage, your model will be garbage — fail fast.
# =============================================================================

@task(
    name="validate_data",
    retries=2,
    retry_delay_seconds=5,
    description="Load dataset and validate schema, nulls, and feature ranges",
)
def validate_data(config: dict) -> dict:
    """Load and validate the dataset.

    This is your lint/static-analysis step. We check:
    1. Schema: correct number of features with expected names
    2. Nulls: no missing values (or handle them if configured)
    3. Ranges: feature values within expected bounds

    If any check fails, the pipeline stops here — same as a lint failure
    blocking your deploy pipeline.
    """
    logger = get_run_logger()
    data_config = config["data"]
    validation_config = data_config["validation"]

    # --- Load data ---
    logger.info("Loading dataset: %s", data_config["source"])
    iris = load_iris()
    feature_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
    df = pd.DataFrame(iris.data, columns=feature_names)
    df["target"] = iris.target

    logger.info("Dataset loaded: %d rows, %d features", len(df), len(feature_names))

    # --- Validation Check 1: Schema ---
    logger.info("Validating schema...")
    actual_features = len(feature_names)
    expected_features = validation_config["expected_features"]
    if actual_features != expected_features:
        raise ValueError(
            f"Schema validation failed: expected {expected_features} features, "
            f"got {actual_features}"
        )
    logger.info("  ✓ Schema valid: %d features", actual_features)

    # --- Validation Check 2: Null values ---
    logger.info("Checking for null values...")
    null_counts = df[feature_names].isnull().sum()
    if not validation_config["allow_nulls"] and null_counts.sum() > 0:
        raise ValueError(
            f"Null validation failed: found nulls in columns: "
            f"{null_counts[null_counts > 0].to_dict()}"
        )
    logger.info("  ✓ No null values found")

    # --- Validation Check 3: Feature ranges ---
    logger.info("Validating feature ranges...")
    for feature, (min_val, max_val) in validation_config["feature_ranges"].items():
        actual_min = df[feature].min()
        actual_max = df[feature].max()
        if actual_min < min_val or actual_max > max_val:
            raise ValueError(
                f"Range validation failed for '{feature}': "
                f"expected [{min_val}, {max_val}], "
                f"got [{actual_min:.2f}, {actual_max:.2f}]"
            )
    logger.info("  ✓ All feature ranges within bounds")

    # --- Split data ---
    X_train, X_test, y_train, y_test = train_test_split(
        df[feature_names],
        df["target"],
        test_size=data_config["test_size"],
        random_state=data_config["random_state"],
    )

    logger.info(
        "Data split: %d train / %d test (%.0f%% test)",
        len(X_train),
        len(X_test),
        data_config["test_size"] * 100,
    )

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": feature_names,
        "n_samples": len(df),
    }


# =============================================================================
# TASK 2: TRAIN MODEL
# =============================================================================
# CI/CD equivalent: BUILD
# Purpose: Transform source material (data) into an artifact (model).
# We log all parameters for reproducibility — same as logging build config.
# =============================================================================

@task(
    name="train_model",
    retries=2,
    retry_delay_seconds=5,
    description="Train model with configured parameters and log all settings",
)
def train_model(data: dict, config: dict) -> dict:
    """Train the model with configured hyperparameters.

    This is your build step. We:
    1. Initialize the model with parameters from config
    2. Train on the training data
    3. Log all parameters for reproducibility

    Every training run should be reproducible — given the same data + config,
    you get the same model. Same principle as deterministic builds.
    """
    logger = get_run_logger()
    model_config = config["model"]
    params = model_config["parameters"]

    logger.info("Training model: %s", model_config["algorithm"])
    logger.info("Parameters:")
    for key, value in params.items():
        logger.info("  %s = %s", key, value)

    # --- Train ---
    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        min_samples_split=params["min_samples_split"],
        min_samples_leaf=params["min_samples_leaf"],
        random_state=params["random_state"],
    )

    model.fit(data["X_train"], data["y_train"])

    logger.info("  ✓ Model trained on %d samples", len(data["X_train"]))
    logger.info(
        "  ✓ Model has %d trees with max_depth=%s",
        params["n_estimators"],
        params["max_depth"],
    )

    return {
        "model": model,
        "parameters": params,
        "algorithm": model_config["algorithm"],
        "training_samples": len(data["X_train"]),
    }


# =============================================================================
# TASK 3: EVALUATE MODEL
# =============================================================================
# CI/CD equivalent: TEST
# Purpose: Quality gate — model must meet accuracy threshold to proceed.
# If metrics are below threshold, the pipeline FAILS here.
# Same as: tests must pass before deploy, coverage must be above X%.
# =============================================================================

@task(
    name="evaluate_model",
    retries=1,
    retry_delay_seconds=3,
    description="Evaluate model and enforce accuracy threshold gate",
)
def evaluate_model(model_result: dict, data: dict, config: dict) -> dict:
    """Evaluate the model and enforce quality gates.

    This is your test step with a hard gate:
    - If accuracy >= threshold → PASS → proceed to registration
    - If accuracy < threshold  → FAIL → pipeline stops, model not promoted

    Same concept as: "tests must pass" or "coverage must be above 80%"
    before code can be deployed.
    """
    logger = get_run_logger()
    eval_config = config["evaluation"]
    threshold = eval_config["min_accuracy_threshold"]

    model = model_result["model"]

    # --- Generate predictions ---
    y_pred = model.predict(data["X_test"])
    y_true = data["y_test"]

    # --- Calculate metrics ---
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_weighted": precision_score(y_true, y_pred, average="weighted"),
        "recall_weighted": recall_score(y_true, y_pred, average="weighted"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
    }

    logger.info("Evaluation results:")
    for metric_name, value in metrics.items():
        logger.info("  %s = %.4f", metric_name, value)

    # --- Quality Gate ---
    logger.info("")
    logger.info("Quality gate: accuracy >= %.2f", threshold)

    if metrics["accuracy"] < threshold:
        # PIPELINE FAILS HERE — same as a test failure blocking deploy
        logger.error(
            "  ✗ FAILED: accuracy %.4f < threshold %.2f",
            metrics["accuracy"],
            threshold,
        )
        logger.error("  Pipeline halted. Model will NOT be registered.")
        raise ValueError(
            f"Quality gate failed: accuracy {metrics['accuracy']:.4f} "
            f"is below threshold {threshold:.2f}. "
            f"Model not promoted. Investigate data quality or tune parameters."
        )

    logger.info(
        "  ✓ PASSED: accuracy %.4f >= threshold %.2f",
        metrics["accuracy"],
        threshold,
    )

    return {
        "metrics": metrics,
        "threshold": threshold,
        "passed": True,
        "test_samples": len(y_true),
    }


# =============================================================================
# TASK 4: REGISTER MODEL
# =============================================================================
# CI/CD equivalent: DEPLOY (to artifact registry)
# Purpose: Save the model artifact + metadata for serving.
# Only runs if evaluation passes — same as deploy only after tests pass.
# =============================================================================

@task(
    name="register_model",
    retries=2,
    retry_delay_seconds=5,
    description="Save model artifact and metadata to registry",
)
def register_model(
    model_result: dict, eval_result: dict, data: dict, config: dict
) -> dict:
    """Register (save) the model to the artifact directory.

    This is your deploy/promotion step. We:
    1. Save the serialized model file
    2. Save metrics for audit trail
    3. Save the config used for this run (reproducibility)

    Only executes if the evaluation gate passed. In production, this would
    push to a model registry (MLflow, Vertex AI, SageMaker) rather than
    a local directory — but the concept is identical.
    """
    logger = get_run_logger()
    registry_config = config["registry"]

    # --- Prepare output directory ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / registry_config["output_dir"] / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Save model artifact ---
    model_path = output_dir / registry_config["model_filename"]
    joblib.dump(model_result["model"], model_path)
    logger.info("  ✓ Model saved: %s", model_path)

    # --- Save metrics (audit trail) ---
    metrics_path = output_dir / registry_config["metrics_filename"]
    metrics_record = {
        "timestamp": timestamp,
        "metrics": eval_result["metrics"],
        "threshold": eval_result["threshold"],
        "passed": eval_result["passed"],
        "training_samples": model_result["training_samples"],
        "test_samples": eval_result["test_samples"],
        "algorithm": model_result["algorithm"],
        "parameters": model_result["parameters"],
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics_record, f, indent=2)
    logger.info("  ✓ Metrics saved: %s", metrics_path)

    # --- Save run config (reproducibility) ---
    config_path = output_dir / registry_config["config_filename"]
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    logger.info("  ✓ Config saved: %s", config_path)

    logger.info("")
    logger.info("═══════════════════════════════════════════════")
    logger.info("  MODEL REGISTERED SUCCESSFULLY")
    logger.info("  Version: %s", timestamp)
    logger.info("  Accuracy: %.4f (threshold: %.2f)", 
                eval_result["metrics"]["accuracy"], eval_result["threshold"])
    logger.info("  Artifacts: %s", output_dir)
    logger.info("═══════════════════════════════════════════════")

    return {
        "version": timestamp,
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "output_dir": str(output_dir),
    }


# =============================================================================
# FLOW: THE FULL PIPELINE
# =============================================================================
# This is the DAG — the orchestration of all tasks in order.
# Prefect's @flow decorator makes this function the pipeline entry point.
# Same as defining your full CI/CD pipeline (stages + dependencies).
# =============================================================================

@flow(
    name="ml-training-pipeline",
    description="End-to-end ML training pipeline: validate → train → evaluate → register",
    retries=0,  # Don't retry the entire pipeline; individual tasks handle retries
)
def ml_training_pipeline(config_path: str = "pipeline_config.yml"):
    """End-to-end ML training pipeline.

    Pipeline stages (same as CI/CD):
        1. validate_data  → Lint:   catch bad inputs early
        2. train_model    → Build:  create the artifact
        3. evaluate_model → Test:   gate on quality metrics
        4. register_model → Deploy: promote to registry

    If any stage fails, subsequent stages don't run.
    This is the same behavior as your GitHub Actions / Jenkins pipeline.
    """
    logger = get_run_logger()

    logger.info("═══════════════════════════════════════════════")
    logger.info("  ML TRAINING PIPELINE — STARTING")
    logger.info("═══════════════════════════════════════════════")
    logger.info("")

    # Load config (pipeline variables)
    config = load_config(config_path)
    logger.info("Config loaded from: %s", config_path)
    logger.info("")

    # --- Stage 1: Validate Data (= Lint) ---
    logger.info("━━━ Stage 1/4: Data Validation ━━━")
    data = validate_data(config)
    logger.info("")

    # --- Stage 2: Train Model (= Build) ---
    logger.info("━━━ Stage 2/4: Model Training ━━━")
    model_result = train_model(data, config)
    logger.info("")

    # --- Stage 3: Evaluate Model (= Test) ---
    logger.info("━━━ Stage 3/4: Model Evaluation ━━━")
    eval_result = evaluate_model(model_result, data, config)
    logger.info("")

    # --- Stage 4: Register Model (= Deploy) ---
    logger.info("━━━ Stage 4/4: Model Registration ━━━")
    registry_result = register_model(model_result, eval_result, data, config)
    logger.info("")

    logger.info("═══════════════════════════════════════════════")
    logger.info("  PIPELINE COMPLETE — ALL STAGES PASSED")
    logger.info("═══════════════════════════════════════════════")

    return registry_result


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Run the pipeline — same as triggering your CI/CD pipeline locally
    result = ml_training_pipeline()

    print("\n" + "=" * 50)
    print("Pipeline finished successfully!")
    print(f"Model artifact: {result['model_path']}")
    print(f"Run metrics:    {result['metrics_path']}")
    print("=" * 50)
