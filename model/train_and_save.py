#!/usr/bin/env python3
"""
Model training script for fraud detection.

This script:
1. Loads the dataset
2. Fits the FraudPreprocessor
3. Trains a RandomForestClassifier
4. Saves model artifacts for API serving
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

from model.preprocessing import FraudPreprocessor


def main() -> None:
    """Train and save fraud detection model."""
    # Configuration
    dataset_path = Path('abuse_dataset_5000_v2.csv')
    artifacts_dir = Path('model/artifacts')

    # Create artifacts directory if it doesn't exist
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("FRAUD DETECTION MODEL TRAINING")
    print("="*60)

    # Load dataset
    print(f"\nLoading dataset from {dataset_path}...")
    if not dataset_path.exists():
        print(f"Error: Dataset not found at {dataset_path}")
        print("Please ensure abuse_dataset_5000_v2.csv exists in the current directory")
        sys.exit(1)

    df = pd.read_csv(dataset_path)
    print(f"Loaded {len(df):,} records")

    # Display class distribution
    print(f"\nClass distribution:")
    print(df['is_abuse'].value_counts())
    print(f"  Legitimate: {(~df['is_abuse']).sum()} ({(~df['is_abuse']).sum() / len(df) * 100:.1f}%)")
    print(f"  Fraudulent: {df['is_abuse'].sum()} ({df['is_abuse'].sum() / len(df) * 100:.1f}%)")

    # Initialize and fit preprocessor
    print("\nFitting preprocessor...")
    preprocessor = FraudPreprocessor()
    X = preprocessor.fit_transform(df)
    y = df['is_abuse'].astype(int)

    print(f"Features: {len(preprocessor.feature_cols)}")
    print(f"Feature columns: {', '.join(preprocessor.feature_cols)}")

    # Split data
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train size: {len(X_train):,}")
    print(f"  Test size: {len(X_test):,}")

    # Train model with same hyperparameters as example
    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("Training complete!")

    # Evaluate model
    print("\n" + "="*60)
    print("MODEL EVALUATION")
    print("="*60)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=['Legitimate', 'Fraudulent']
    ))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives (Legit correctly predicted):  {cm[0, 0]:4d}")
    print(f"  False Positives (Legit wrongly flagged):     {cm[0, 1]:4d}")
    print(f"  False Negatives (Fraud missed):              {cm[1, 0]:4d}")
    print(f"  True Positives (Fraud correctly detected):   {cm[1, 1]:4d}")

    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:35s} {row['importance']:.4f}")

    # Save artifacts
    print("\n" + "="*60)
    print("SAVING MODEL ARTIFACTS")
    print("="*60)

    model_path = artifacts_dir / 'fraud_model.joblib'
    preprocessor_path = artifacts_dir / 'preprocessor.joblib'
    metadata_path = artifacts_dir / 'metadata.json'

    # Save model
    print(f"\nSaving model to {model_path}...")
    joblib.dump(model, model_path)

    # Save preprocessor
    print(f"Saving preprocessor to {preprocessor_path}...")
    joblib.dump(preprocessor, preprocessor_path)

    # Create metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'model_version': '1.0.0',
        'dataset': str(dataset_path),
        'n_samples': len(df),
        'n_features': len(preprocessor.feature_cols),
        'feature_names': preprocessor.feature_cols,
        'model_classes': model.classes_.tolist(),
        'model_params': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 20,
            'random_state': 42
        },
        'test_accuracy': float((y_pred == y_test).mean()),
        'test_samples': len(X_test)
    }

    print(f"Saving metadata to {metadata_path}...")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"\nArtifacts saved to {artifacts_dir}/")
    print(f"  - {model_path.name}")
    print(f"  - {preprocessor_path.name}")
    print(f"  - {metadata_path.name}")
    print("\nYou can now start the API server with:")
    print("  uv run uvicorn api.main:app --reload --port 8000")


if __name__ == '__main__':
    main()
