"""
FastAPI application for fraud detection.
"""
import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from api.models import (
    TransactionRequest,
    FraudPredictionResponse,
    HealthResponse,
    ModelInfoResponse
)
from api.predictor import FraudPredictor


# Global state to hold loaded model artifacts
ml_models: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to load model artifacts at startup.
    """
    artifacts_dir = Path('model/artifacts')

    print("Loading model artifacts...")

    try:
        # Load model
        model_path = artifacts_dir / 'fraud_model.joblib'
        print(f"  Loading model from {model_path}")
        ml_models['model'] = joblib.load(model_path)

        # Load preprocessor
        preprocessor_path = artifacts_dir / 'preprocessor.joblib'
        print(f"  Loading preprocessor from {preprocessor_path}")
        ml_models['preprocessor'] = joblib.load(preprocessor_path)

        # Load metadata
        metadata_path = artifacts_dir / 'metadata.json'
        print(f"  Loading metadata from {metadata_path}")
        with open(metadata_path, 'r') as f:
            ml_models['metadata'] = json.load(f)

        # Initialize predictor
        ml_models['predictor'] = FraudPredictor(
            model=ml_models['model'],
            preprocessor=ml_models['preprocessor'],
            metadata=ml_models['metadata']
        )

        print("✓ Model artifacts loaded successfully!")
        print(f"  Model version: {ml_models['metadata'].get('model_version')}")
        print(f"  Training date: {ml_models['metadata'].get('training_date')}")
        print(f"  Features: {ml_models['metadata'].get('n_features')}")

    except FileNotFoundError as e:
        print(f"✗ Error: Model artifacts not found - {e}")
        print("\nPlease train the model first:")
        print("  uv run python -m model.train_and_save")
        raise

    except Exception as e:
        print(f"✗ Error loading model artifacts: {e}")
        raise

    yield

    # Cleanup (if needed)
    ml_models.clear()
    print("Model artifacts unloaded")


# Create FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection for e-commerce transactions",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "model_info": "/api/v1/model/info"
    }


@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the service status and whether the model is loaded.
    """
    model_loaded = 'predictor' in ml_models and ml_models['predictor'] is not None

    return HealthResponse(
        status='healthy' if model_loaded else 'unhealthy',
        model_loaded=model_loaded
    )


@app.get(
    "/api/v1/model/info",
    response_model=ModelInfoResponse,
    tags=["Model"]
)
async def model_info() -> ModelInfoResponse:
    """
    Get model metadata.

    Returns information about the currently loaded model including
    training date, version, and features used.
    """
    if 'metadata' not in ml_models:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )

    metadata = ml_models['metadata']

    return ModelInfoResponse(
        model_version=metadata.get('model_version', 'unknown'),
        training_date=metadata.get('training_date', 'unknown'),
        n_features=metadata.get('n_features', 0),
        feature_names=metadata.get('feature_names', []),
        model_classes=metadata.get('model_classes', [])
    )


@app.post(
    "/api/v1/predict",
    response_model=FraudPredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"]
)
async def predict_fraud(
    transaction: TransactionRequest
) -> FraudPredictionResponse:
    """
    Score a transaction for fraud.

    Returns a legitimacy score between 0.0 (definitely fraud) and 1.0
    (definitely legitimate), along with a binary prediction and confidence score.

    Args:
        transaction: Transaction data to score

    Returns:
        Fraud prediction with legitimacy score

    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    if 'predictor' not in ml_models:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please ensure the server started correctly."
        )

    try:
        prediction = ml_models['predictor'].predict(transaction)
        return prediction

    except Exception as e:
        # Log the error in production, you'd want proper logging here
        print(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )
