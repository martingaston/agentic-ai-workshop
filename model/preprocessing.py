"""
Shared preprocessing module for fraud detection.

This module ensures consistent feature transformations between training and serving,
preventing train/serve skew.
"""
from typing import Union, Dict, Any
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np


class FraudPreprocessor:
    """
    Encapsulates all feature transformations for fraud detection.

    This class ensures that the exact same transformations are applied during
    both training and serving (API inference).
    """

    def __init__(self) -> None:
        """Initialize the preprocessor with label encoders."""
        self.le_email = LabelEncoder()
        self.le_device = LabelEncoder()
        self.le_payment = LabelEncoder()
        self.le_cvv = LabelEncoder()
        self.le_avs = LabelEncoder()
        self.le_processor = LabelEncoder()

        self.is_fitted = False

        # Boolean columns that need to be converted to integers
        self.bool_cols = [
            'phone_verified', 'email_verified', 'profile_complete',
            'new_device', 'vpn_proxy_detected', 'billing_shipping_match',
            'high_risk_category', 'is_abuse'
        ]

        # Feature columns used in the model (must match training order)
        self.feature_cols = [
            # Account features
            'account_age_days',
            'email_domain_encoded',
            'phone_verified',
            'email_verified',
            'profile_complete',
            'failed_login_attempts_24h',
            'successful_logins_7d',
            'password_reset_count_30d',

            # Device features
            'device_type_encoded',
            'new_device',
            'vpn_proxy_detected',

            # Payment features
            'payment_method_encoded',
            'billing_shipping_match',
            'cvv_check_encoded',
            'avs_result_encoded',
            'processor_response_encoded',

            # Behavioral features
            'days_since_account_first_purchase',
            'total_orders_lifetime',
            'orders_last_24h',
            'orders_last_7d',
            'session_duration_seconds',
            'cart_additions_session',
            'high_risk_category',

            # Order features
            'order_amount',
        ]

    def fit(self, df: pd.DataFrame) -> 'FraudPreprocessor':
        """
        Fit the preprocessor on training data.

        Args:
            df: Training DataFrame containing all necessary columns

        Returns:
            Self for method chaining
        """
        # Fit label encoders on categorical columns
        self.le_email.fit(df['email_domain'])
        self.le_device.fit(df['device_type'])
        self.le_payment.fit(df['payment_method'])
        self.le_cvv.fit(df['cvv_check_result'])
        self.le_avs.fit(df['avs_result'])
        self.le_processor.fit(df['payment_processor_response'])

        self.is_fitted = True
        return self

    def transform(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
        """
        Transform input data using fitted encoders.

        Args:
            data: Either a DataFrame or dict containing transaction data

        Returns:
            Transformed DataFrame with encoded features

        Raises:
            ValueError: If preprocessor hasn't been fitted yet
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        # Convert dict to DataFrame if necessary
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()

        # Convert boolean columns to integers
        for col in self.bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)

        # Encode categorical features with unknown value handling
        df['email_domain_encoded'] = self._safe_transform(
            self.le_email, df['email_domain'], 'email_domain'
        )
        df['device_type_encoded'] = self._safe_transform(
            self.le_device, df['device_type'], 'device_type'
        )
        df['payment_method_encoded'] = self._safe_transform(
            self.le_payment, df['payment_method'], 'payment_method'
        )
        df['cvv_check_encoded'] = self._safe_transform(
            self.le_cvv, df['cvv_check_result'], 'cvv_check_result'
        )
        df['avs_result_encoded'] = self._safe_transform(
            self.le_avs, df['avs_result'], 'avs_result'
        )
        df['processor_response_encoded'] = self._safe_transform(
            self.le_processor, df['payment_processor_response'], 'payment_processor_response'
        )

        # Select only the feature columns used in training
        return df[self.feature_cols]

    def _safe_transform(
        self,
        encoder: LabelEncoder,
        values: pd.Series,
        column_name: str
    ) -> pd.Series:
        """
        Safely transform categorical values, handling unknown categories.

        For unknown categories not seen during training, assigns a default encoding (0)
        and logs a warning.

        Args:
            encoder: Fitted LabelEncoder
            values: Series of categorical values to encode
            column_name: Name of the column (for logging)

        Returns:
            Series of encoded integer values
        """
        result = np.zeros(len(values), dtype=int)
        known_classes = set(encoder.classes_)

        for idx, value in enumerate(values):
            if value in known_classes:
                result[idx] = encoder.transform([value])[0]
            else:
                # Unknown category - assign default encoding
                result[idx] = 0
                print(f"Warning: Unknown {column_name} value '{value}' - assigning default encoding")

        return pd.Series(result, index=values.index)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit the preprocessor and transform the data in one step.

        Args:
            df: Training DataFrame

        Returns:
            Transformed DataFrame
        """
        return self.fit(df).transform(df)
