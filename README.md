# Synthetic Ecommerce Abuse Detection Dataset

A Python-based generator for creating realistic synthetic datasets to train ML models for detecting account abuse and payment fraud in ecommerce platforms.

## Overview

This tool generates CSV datasets with realistic patterns for:
- **Legitimate transactions** (~75% of data)
- **Fake account abuse** (~10% of data) - New accounts with temporary emails, unverified profiles
- **Account takeover** (~8% of data) - Established accounts with suspicious device/location changes
- **Payment fraud** (~7% of data) - Geographic mismatches, failed verification, high-risk items

## Features

- **40+ realistic features** including account, device, network, payment, and behavioral signals
- **Pattern-based generation** with characteristic distributions for each abuse type
- **Configurable class distributions** to match your training needs
- **Reproducible** with random seed support
- **Validation** with built-in quality checks
- **Scalable** - generate 10K to 100K+ records

## Quick Start

### Installation

```bash
# Clone or download this repository
cd abuse-workshop

# Install dependencies
uv add faker pandas numpy
```

### Generate a Dataset

```bash
# Generate 50,000 records with default distribution
uv run python -m data.generate_synthetic_data --size 50000

# Custom distribution
uv run python -m data.generate_synthetic_data --size 100000 \
    --legitimate-ratio 0.80 \
    --fake-account-ratio 0.10 \
    --account-takeover-ratio 0.06 \
    --payment-fraud-ratio 0.04 \
    --output my_dataset.csv
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--size` | Number of records to generate | 50000 |
| `--output` | Output CSV file path | abuse_dataset_<size>.csv |
| `--seed` | Random seed for reproducibility | 42 |
| `--legitimate-ratio` | Proportion of legitimate transactions | 0.75 |
| `--fake-account-ratio` | Proportion of fake account abuse | 0.10 |
| `--account-takeover-ratio` | Proportion of account takeover | 0.08 |
| `--payment-fraud-ratio` | Proportion of payment fraud | 0.07 |
| `--no-validate` | Skip validation checks | False |

## Dataset Schema

### Core Transaction Fields
- `transaction_id` - Unique transaction identifier
- `timestamp` - Transaction timestamp
- `user_id` - Unique user identifier
- `order_amount` - Total order value in USD
- `currency` - Currency code

### Account-Related Fields (Account Abuse Detection)
- `account_created_date` - When account was created
- `account_age_days` - Days since account creation
- `email_domain` - Domain of email address
- `phone_verified` - Whether phone is verified
- `email_verified` - Whether email is verified
- `profile_complete` - Profile has photo and bio
- `failed_login_attempts_24h` - Failed logins in last 24h
- `successful_logins_7d` - Successful logins in last 7 days
- `password_reset_count_30d` - Password resets in last 30 days

### Device & Network Fields (Account Takeover Detection)
- `device_id` - Unique device identifier
- `ip_address` - IP address (anonymized)
- `ip_country` - Country from IP geolocation
- `user_agent` - Browser/device user agent
- `device_type` - Type of device (desktop, mobile, tablet)
- `new_device` - First time seeing this device
- `vpn_proxy_detected` - VPN or proxy detected

### Payment Fields (Payment Fraud Detection)
- `payment_method` - Payment type (credit_card, debit_card, paypal, crypto)
- `card_bin` - First 6 digits of card
- `card_country` - Card issuing country
- `billing_country` - Billing address country
- `shipping_country` - Shipping address country
- `billing_shipping_match` - Billing and shipping match
- `cvv_check_result` - CVV verification result
- `avs_result` - Address verification result
- `payment_processor_response` - Processor response code

### Behavioral & Velocity Fields
- `days_since_account_first_purchase` - Days from account creation to first purchase
- `total_orders_lifetime` - Total orders by this user
- `orders_last_24h` - Orders in last 24 hours
- `orders_last_7d` - Orders in last 7 days
- `avg_order_value` - Average historical order value
- `session_duration_seconds` - Time spent in current session
- `cart_additions_session` - Items added to cart this session
- `high_risk_category` - Order contains high-risk items

### Target Labels
- `is_abuse` - Whether transaction is abusive (boolean)
- `abuse_type` - Specific type: legitimate, fake_account, account_takeover, payment_fraud
- `abuse_confidence` - Confidence score 0.0 to 1.0

## Abuse Pattern Characteristics

### Legitimate Transactions
- Normal account age (30+ days)
- Verified email/phone
- Consistent device/IP patterns
- Reasonable order velocity
- Matching billing/shipping addresses
- Clean payment verification

### Fake Account Patterns
- Very new accounts (0-3 days old)
- Temporary email domains (tempmail.net, guerrillamail.com)
- No phone/email verification
- Incomplete profiles
- First purchase immediately after account creation
- High VPN usage

### Account Takeover Patterns
- Established accounts (90+ days old)
- Multiple failed login attempts
- Recent password reset
- New device/location suddenly appearing
- Shipping to different country than usual
- Higher than average order value

### Payment Fraud Patterns
- Billing/shipping address mismatch
- Card country doesn't match IP country
- Failed CVV or AVS checks
- Multiple payment attempts
- High-risk items (electronics, gift cards)
- Very high order value

## Example Usage

### Running the Example ML Pipeline

```bash
# Generate a dataset
uv run python -m data.generate_synthetic_data --size 10000

# Run the example ML pipeline
uv run python -m model.example_ml_pipeline abuse_dataset_10000.csv
```

### Basic ML Pipeline (Custom Code)

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load dataset
df = pd.read_csv('abuse_dataset_50000.csv')

# Prepare features (example - you'll want more sophisticated feature engineering)
feature_cols = [
    'account_age_days', 'email_verified', 'phone_verified',
    'failed_login_attempts_24h', 'new_device', 'vpn_proxy_detected',
    'billing_shipping_match', 'orders_last_24h', 'high_risk_category'
]

X = df[feature_cols]
y = df['is_abuse']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
```

## Dataset Validation

The generator includes built-in validation checks:
- No null values in required fields
- Class distribution matches targets
- Numeric ranges are valid (e.g., account_age_days >= 0)
- Pattern characteristics match abuse type definitions
- Statistical summaries by abuse type

## File Structure

```
abuse-workshop/
├── data/
│   ├── generate_synthetic_data.py  # Main generation script
│   └── patterns.py                 # Pattern generators for each abuse type
├── model/
│   ├── artifacts/                  # Trained model files (committed for workshop simplicity)
│   │   ├── fraud_model.joblib      # Trained classifier
│   │   ├── preprocessor.joblib     # Feature preprocessor
│   │   └── metadata.json           # Model metadata
│   ├── example_ml_pipeline.py      # Example ML training pipeline
│   ├── train_and_save.py           # Model training script
│   └── preprocessing.py            # Feature preprocessing
├── api/
│   ├── main.py                     # FastAPI application
│   ├── models.py                   # Request/response models
│   └── predictor.py                # Prediction logic
├── schema.py                       # Data schema and constants
├── README.md                       # This file
└── *.csv                           # Generated datasets (not in git)
```

**Note on Model Artifacts:** For this workshop, trained model files are committed to the repository for simplicity. In production, model artifacts should **not** be committed to git because they:
- Are large binary files that bloat the repository
- Change frequently during retraining cycles
- Don't diff well in version control
- Should be stored in dedicated model registries (e.g., MLflow, W&B, AWS SageMaker Model Registry, Azure ML Model Registry)

For production deployments, regenerate models using `uv run python -m model.train_and_save` or fetch them from your model registry.

## Design Rationale

1. **Multi-layered features**: Combines account, behavioral, and payment features to enable detection of different abuse types
2. **Temporal features**: Account age and velocity metrics are critical for detecting suspicious patterns
3. **Geographic signals**: IP, card, billing, shipping country mismatches are strong fraud indicators
4. **Verification signals**: Email/phone verification status helps distinguish fake accounts
5. **Soft labels**: Abuse confidence score allows for uncertainty, more realistic for ML training
6. **Realistic distributions**: Pattern generators use empirically-inspired distributions, not perfect separations

## Limitations

This is **synthetic data** designed for educational purposes and initial model prototyping. Real-world fraud detection systems require:
- Training on actual transaction data with verified labels
- Handling of data drift and evolving attack patterns
- Integration with real-time scoring systems
- Compliance with privacy regulations (GDPR, CCPA)
- Human review workflows for high-risk transactions

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to submit issues or pull requests to improve the dataset generator.
