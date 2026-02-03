"""
Prediction orchestration for fraud detection.
"""
from typing import Any, Dict

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from api.models import TransactionRequest, FraudPredictionResponse
from model.preprocessing import FraudPreprocessor


class FraudPredictor:
    """
    Orchestrates fraud prediction using the trained model and preprocessor.
    """

    def __init__(
        self,
        model: RandomForestClassifier,
        preprocessor: FraudPreprocessor,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Initialize the predictor.

        Args:
            model: Trained RandomForestClassifier
            preprocessor: Fitted FraudPreprocessor
            metadata: Model metadata dictionary
        """
        self.model = model
        self.preprocessor = preprocessor
        self.metadata = metadata

        # Determine the index of the legitimate class (class 0)
        # model.classes_ is typically [0, 1] where 0=legitimate, 1=fraud
        self.legitimate_class_idx = np.where(model.classes_ == 0)[0][0]

    def predict(self, transaction: TransactionRequest) -> FraudPredictionResponse:
        """
        Score a transaction for fraud.

        Args:
            transaction: Pydantic model containing transaction data

        Returns:
            Fraud prediction response with legitimacy score
        """
        # Convert Pydantic model to dictionary
        transaction_dict = transaction.model_dump()

        # Transform features using the fitted preprocessor
        features = self.preprocessor.transform(transaction_dict)

        # Get prediction probabilities
        # Shape: (1, 2) for binary classification [prob_class_0, prob_class_1]
        probabilities = self.model.predict_proba(features)[0]

        # Extract legitimacy score (probability of class 0)
        legitimacy_score = float(probabilities[self.legitimate_class_idx])

        # Determine binary prediction
        prediction = 'legitimate' if legitimacy_score >= 0.5 else 'fraud'

        # Confidence is the maximum probability
        confidence = float(max(probabilities))

        return FraudPredictionResponse(
            transaction_id=transaction.transaction_id,
            legitimacy_score=legitimacy_score,
            prediction=prediction,
            confidence=confidence,
            model_version=self.metadata.get('model_version', 'unknown')
        )
