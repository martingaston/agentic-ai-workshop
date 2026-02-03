#!/usr/bin/env python3
"""
Example ML pipeline using the synthetic abuse detection dataset.

This demonstrates basic feature engineering and model training for
detecting account abuse and payment fraud.
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder


def load_and_prepare_data(csv_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """
    Load dataset and prepare features for modeling.

    Args:
        csv_path: Path to the CSV dataset

    Returns:
        Tuple of (feature DataFrame, full DataFrame, target Series)
    """
    # Load dataset
    df = pd.read_csv(csv_path)

    print(f"Loaded {len(df):,} records")
    print(f"\nClass distribution:")
    print(df['abuse_type'].value_counts())

    # Convert boolean columns to integers
    bool_cols = [
        'phone_verified', 'email_verified', 'profile_complete',
        'new_device', 'vpn_proxy_detected', 'billing_shipping_match',
        'high_risk_category', 'is_abuse'
    ]
    for col in bool_cols:
        df[col] = df[col].astype(int)

    # Encode categorical features
    le_email = LabelEncoder()
    df['email_domain_encoded'] = le_email.fit_transform(df['email_domain'])

    le_device = LabelEncoder()
    df['device_type_encoded'] = le_device.fit_transform(df['device_type'])

    le_payment = LabelEncoder()
    df['payment_method_encoded'] = le_payment.fit_transform(df['payment_method'])

    le_cvv = LabelEncoder()
    df['cvv_check_encoded'] = le_cvv.fit_transform(df['cvv_check_result'])

    le_avs = LabelEncoder()
    df['avs_result_encoded'] = le_avs.fit_transform(df['avs_result'])

    le_processor = LabelEncoder()
    df['processor_response_encoded'] = le_processor.fit_transform(df['payment_processor_response'])

    # Select features for modeling
    feature_cols = [
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

    X = df[feature_cols]
    y = df['is_abuse']

    print(f"\nUsing {len(feature_cols)} features")

    return X, df, y


def train_binary_classifier(X: pd.DataFrame, y: pd.Series) -> None:
    """
    Train a binary classifier to detect abuse vs legitimate transactions.

    Args:
        X: Feature DataFrame
        y: Target Series (is_abuse)
    """
    print("\n" + "="*60)
    print("BINARY CLASSIFICATION: Abuse vs Legitimate")
    print("="*60)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nTrain size: {len(X_train):,}")
    print(f"Test size: {len(X_test):,}")

    # Train model
    print("\nTraining Random Forest classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Predictions
    y_pred = clf.predict(X_test)

    # Evaluation
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Abuse']))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"True Negatives (Legit correctly predicted):  {cm[0, 0]}")
    print(f"False Positives (Legit wrongly flagged):     {cm[0, 1]}")
    print(f"False Negatives (Abuse missed):              {cm[1, 0]}")
    print(f"True Positives (Abuse correctly detected):   {cm[1, 1]}")

    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)

    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']:35s} {row['importance']:.4f}")


def train_multiclass_classifier(X: pd.DataFrame, df: pd.DataFrame) -> None:
    """
    Train a multiclass classifier to detect specific abuse types.

    Args:
        X: Feature DataFrame
        df: Full DataFrame with abuse_type column
    """
    print("\n" + "="*60)
    print("MULTICLASS CLASSIFICATION: Abuse Type Detection")
    print("="*60)

    y_multi = df['abuse_type']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_multi, test_size=0.2, random_state=42, stratify=y_multi
    )

    # Train model
    print("\nTraining Random Forest multiclass classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Predictions
    y_pred = clf.predict(X_test)

    # Evaluation
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=['legitimate', 'fake_account', 'account_takeover', 'payment_fraud'])
    print(pd.DataFrame(
        cm,
        index=['True: Legit', 'True: Fake Acct', 'True: Takeover', 'True: Fraud'],
        columns=['Pred: Legit', 'Pred: Fake Acct', 'Pred: Takeover', 'Pred: Fraud']
    ))


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run example_ml_pipeline.py <dataset.csv>")
        print("\nExample:")
        print("  uv run example_ml_pipeline.py test_dataset.csv")
        sys.exit(1)

    csv_path = sys.argv[1]

    print("="*60)
    print("ABUSE DETECTION ML PIPELINE")
    print("="*60)

    # Load and prepare data
    X, df, y = load_and_prepare_data(csv_path)

    # Train binary classifier
    train_binary_classifier(X, y)

    # Train multiclass classifier
    train_multiclass_classifier(X, df)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
