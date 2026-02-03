"""
Schema definitions for synthetic ecommerce abuse detection dataset.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class TransactionRecord:
    """Represents a single transaction record in the dataset."""

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

    # Target Labels
    is_abuse: bool
    abuse_type: Literal['legitimate', 'suspicious_but_legitimate', 'fake_account', 'account_takeover', 'payment_fraud']
    abuse_confidence: float
    difficulty_tier: Literal['easy', 'medium', 'hard', 'n/a']  # Fraud detection difficulty (n/a for legitimate)

    def to_dict(self) -> dict:
        """Convert record to dictionary for CSV export."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime):
                result[field_name] = field_value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                result[field_name] = field_value
        return result


# Common data constants
TEMP_EMAIL_DOMAINS = [
    'tempmail.net', 'guerrillamail.com', '10minutemail.com',
    'throwaway.email', 'mailinator.com', 'temp-mail.org'
]

LEGITIMATE_EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'icloud.com', 'protonmail.com', 'aol.com'
]

HIGH_RISK_COUNTRIES = [
    'RU', 'NG', 'CN', 'PK', 'ID', 'UA', 'VN'
]

LOW_RISK_COUNTRIES = [
    'US', 'CA', 'GB', 'AU', 'DE', 'FR', 'JP', 'SE', 'NL', 'CH'
]

DEVICE_TYPES = ['desktop', 'mobile', 'tablet']

PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'crypto']

USER_AGENTS = [
    'Chrome/120.0',
    'Firefox/121.0',
    'Safari/17.0',
    'Edge/120.0',
    'Mobile Safari/16.0',
    'Chrome Mobile/120.0',
    'Bot/1.0',
    'curl/7.68.0'
]

# Card BIN prefixes (first 6 digits)
VISA_BINS = ['424242', '411111', '440000', '456789']
MASTERCARD_BINS = ['540123', '555555', '522222', '510000']
AMEX_BINS = ['378282', '371449', '370000']
DISCOVER_BINS = ['601100', '644444', '650000']

ALL_CARD_BINS = VISA_BINS + MASTERCARD_BINS + AMEX_BINS + DISCOVER_BINS
