"""
Pydantic models for API request/response validation.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """
    Request schema for fraud prediction.

    Matches the TransactionRecord schema from schema.py, but excludes
    the target labels (is_abuse, abuse_type, etc.).
    """
    # Core Transaction Fields
    transaction_id: str
    timestamp: datetime
    user_id: str
    order_amount: float
    currency: str

    # Account-Related Fields
    account_created_date: datetime
    account_age_days: int
    email_domain: str
    phone_verified: bool
    email_verified: bool
    profile_complete: bool
    failed_login_attempts_24h: int
    successful_logins_7d: int
    password_reset_count_30d: int

    # Device & Network Fields
    device_id: str
    ip_address: str
    ip_country: str
    user_agent: str
    device_type: Literal['desktop', 'mobile', 'tablet']
    new_device: bool
    vpn_proxy_detected: bool

    # Payment Fields
    payment_method: Literal['credit_card', 'debit_card', 'paypal', 'crypto']
    card_bin: str
    card_country: str
    billing_country: str
    shipping_country: str
    billing_shipping_match: bool
    cvv_check_result: Literal['pass', 'fail', 'not_checked']
    avs_result: Literal['full_match', 'partial_match', 'no_match']
    payment_processor_response: Literal['approved', 'declined', 'suspected_fraud']

    # Behavioral & Velocity Fields
    days_since_account_first_purchase: int
    total_orders_lifetime: int
    orders_last_24h: int
    orders_last_7d: int
    avg_order_value: float
    session_duration_seconds: int
    cart_additions_session: int
    high_risk_category: bool

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "timestamp": "2024-01-15T14:30:00",
                "user_id": "user_123",
                "order_amount": 149.99,
                "currency": "USD",
                "account_created_date": "2023-06-01T10:00:00",
                "account_age_days": 228,
                "email_domain": "gmail.com",
                "phone_verified": True,
                "email_verified": True,
                "profile_complete": True,
                "failed_login_attempts_24h": 0,
                "successful_logins_7d": 5,
                "password_reset_count_30d": 0,
                "device_id": "dev_abc123",
                "ip_address": "192.168.1.1",
                "ip_country": "US",
                "user_agent": "Chrome/120.0",
                "device_type": "desktop",
                "new_device": False,
                "vpn_proxy_detected": False,
                "payment_method": "credit_card",
                "card_bin": "424242",
                "card_country": "US",
                "billing_country": "US",
                "shipping_country": "US",
                "billing_shipping_match": True,
                "cvv_check_result": "pass",
                "avs_result": "full_match",
                "payment_processor_response": "approved",
                "days_since_account_first_purchase": 180,
                "total_orders_lifetime": 12,
                "orders_last_24h": 1,
                "orders_last_7d": 2,
                "avg_order_value": 125.50,
                "session_duration_seconds": 300,
                "cart_additions_session": 3,
                "high_risk_category": False
            }
        }


class FraudPredictionResponse(BaseModel):
    """Response schema for fraud prediction."""
    transaction_id: str = Field(
        description="The transaction ID from the request"
    )
    legitimacy_score: float = Field(
        description="Probability that transaction is legitimate (0.0=fraud, 1.0=legitimate)",
        ge=0.0,
        le=1.0
    )
    prediction: Literal['legitimate', 'fraud'] = Field(
        description="Binary prediction label"
    )
    confidence: float = Field(
        description="Absolute confidence score (max probability across both classes)",
        ge=0.0,
        le=1.0
    )
    model_version: str = Field(
        description="Version of the model used for prediction"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_12345",
                "legitimacy_score": 0.92,
                "prediction": "legitimate",
                "confidence": 0.92,
                "model_version": "1.0.0"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: Literal['healthy', 'unhealthy']
    model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.now)


class ModelInfoResponse(BaseModel):
    """Response schema for model metadata endpoint."""
    model_version: str
    training_date: str
    n_features: int
    feature_names: list[str]
    model_classes: list[int]
