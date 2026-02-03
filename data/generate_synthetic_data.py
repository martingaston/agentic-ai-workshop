#!/usr/bin/env python3
"""
Generate synthetic ecommerce abuse detection dataset.

This script creates a CSV dataset with realistic patterns for:
- Legitimate transactions
- Fake account abuse
- Account takeover
- Payment fraud

Usage:
    uv run python -m data.generate_synthetic_data --size 50000 --output abuse_dataset_50000.csv
"""
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd
from faker import Faker

from schema import TransactionRecord
from data.patterns import (
    LegitimatePatternGenerator,
    FakeAccountPatternGenerator,
    AccountTakeoverPatternGenerator,
    PaymentFraudPatternGenerator,
)


def generate_timestamp(
    start_date: datetime,
    end_date: datetime
) -> datetime:
    """Generate a random timestamp between start and end dates."""
    time_delta = end_date - start_date
    random_seconds = random.randint(0, int(time_delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)


def generate_dataset(
    size: int,
    legitimate_ratio: float = 0.75,
    fake_account_ratio: float = 0.10,
    account_takeover_ratio: float = 0.08,
    payment_fraud_ratio: float = 0.07,
    seed: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> pd.DataFrame:
    """
    Generate synthetic dataset with specified size and class distribution.

    Args:
        size: Total number of records to generate
        legitimate_ratio: Proportion of legitimate transactions (default: 0.75)
        fake_account_ratio: Proportion of fake account abuse (default: 0.10)
        account_takeover_ratio: Proportion of account takeover (default: 0.08)
        payment_fraud_ratio: Proportion of payment fraud (default: 0.07)
        seed: Random seed for reproducibility
        start_date: Start date for transaction timestamps (default: 90 days ago)
        end_date: End date for transaction timestamps (default: now)

    Returns:
        DataFrame with generated transaction records
    """
    # Validate ratios sum to approximately 1.0
    total_ratio = legitimate_ratio + fake_account_ratio + account_takeover_ratio + payment_fraud_ratio
    if not (0.99 <= total_ratio <= 1.01):
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")

    # Set random seeds for reproducibility
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # Initialize pattern generators
    legit_gen = LegitimatePatternGenerator(seed=seed)
    fake_gen = FakeAccountPatternGenerator(seed=seed)
    takeover_gen = AccountTakeoverPatternGenerator(seed=seed)
    fraud_gen = PaymentFraudPatternGenerator(seed=seed)

    # Set date range for transactions
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=90)

    # Calculate counts for each abuse type
    legitimate_count = int(size * legitimate_ratio)
    fake_account_count = int(size * fake_account_ratio)
    account_takeover_count = int(size * account_takeover_ratio)
    payment_fraud_count = size - legitimate_count - fake_account_count - account_takeover_count

    print(f"Generating {size} records:")
    print(f"  - Legitimate: {legitimate_count} ({legitimate_count/size*100:.1f}%)")
    print(f"  - Fake accounts: {fake_account_count} ({fake_account_count/size*100:.1f}%)")
    print(f"  - Account takeover: {account_takeover_count} ({account_takeover_count/size*100:.1f}%)")
    print(f"  - Payment fraud: {payment_fraud_count} ({payment_fraud_count/size*100:.1f}%)")

    records: List[TransactionRecord] = []

    # Generate legitimate transactions
    print("\nGenerating legitimate transactions...")
    for i in range(legitimate_count):
        if (i + 1) % 5000 == 0:
            print(f"  {i + 1}/{legitimate_count}")
        timestamp = generate_timestamp(start_date, end_date)
        record_data = legit_gen.generate(timestamp)
        records.append(TransactionRecord(**record_data))

    # Generate fake account transactions
    print(f"\nGenerating fake account transactions...")
    for i in range(fake_account_count):
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{fake_account_count}")
        timestamp = generate_timestamp(start_date, end_date)
        record_data = fake_gen.generate(timestamp)
        records.append(TransactionRecord(**record_data))

    # Generate account takeover transactions
    print(f"\nGenerating account takeover transactions...")
    for i in range(account_takeover_count):
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{account_takeover_count}")
        timestamp = generate_timestamp(start_date, end_date)
        record_data = takeover_gen.generate(timestamp)
        records.append(TransactionRecord(**record_data))

    # Generate payment fraud transactions
    print(f"\nGenerating payment fraud transactions...")
    for i in range(payment_fraud_count):
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{payment_fraud_count}")
        timestamp = generate_timestamp(start_date, end_date)
        record_data = fraud_gen.generate(timestamp)
        records.append(TransactionRecord(**record_data))

    # Convert to DataFrame
    print("\nConverting to DataFrame...")
    df = pd.DataFrame([record.to_dict() for record in records])

    # Shuffle records to mix abuse types
    print("Shuffling records...")
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    return df


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate the generated dataset for basic quality checks.

    Args:
        df: DataFrame to validate
    """
    print("\n" + "="*60)
    print("DATASET VALIDATION")
    print("="*60)

    # Check for null values
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\nWARNING: Null values found:")
        print(null_counts[null_counts > 0])
    else:
        print("\n✓ No null values found")

    # Check class distribution
    print("\n--- Class Distribution ---")
    print(df['abuse_type'].value_counts())
    print("\nProportions:")
    print(df['abuse_type'].value_counts(normalize=True))

    # Check is_abuse flag consistency
    abuse_flag_check = df.groupby('abuse_type')['is_abuse'].all()
    if abuse_flag_check['legitimate'] == False and abuse_flag_check.drop('legitimate').all():
        print("\n✓ is_abuse flag consistent with abuse_type")
    else:
        print("\nWARNING: is_abuse flag inconsistent with abuse_type")

    # Numeric range validation
    print("\n--- Numeric Range Validation ---")
    if (df['account_age_days'] >= 0).all():
        print("✓ account_age_days >= 0")
    else:
        print("✗ account_age_days has negative values")

    if (df['order_amount'] > 0).all():
        print("✓ order_amount > 0")
    else:
        print("✗ order_amount has non-positive values")

    if ((df['abuse_confidence'] >= 0) & (df['abuse_confidence'] <= 1)).all():
        print("✓ abuse_confidence in [0, 1]")
    else:
        print("✗ abuse_confidence out of range")

    # Pattern validation - sample records
    print("\n--- Pattern Validation (Sample Records) ---")
    print("\nSample Fake Account Record:")
    fake_sample = df[df['abuse_type'] == 'fake_account'].iloc[0]
    print(f"  Account age: {fake_sample['account_age_days']} days")
    print(f"  Email domain: {fake_sample['email_domain']}")
    print(f"  Email verified: {fake_sample['email_verified']}")
    print(f"  Phone verified: {fake_sample['phone_verified']}")

    print("\nSample Account Takeover Record:")
    takeover_sample = df[df['abuse_type'] == 'account_takeover'].iloc[0]
    print(f"  Account age: {takeover_sample['account_age_days']} days")
    print(f"  Failed login attempts 24h: {takeover_sample['failed_login_attempts_24h']}")
    print(f"  New device: {takeover_sample['new_device']}")
    print(f"  Password resets 30d: {takeover_sample['password_reset_count_30d']}")

    print("\nSample Payment Fraud Record:")
    fraud_sample = df[df['abuse_type'] == 'payment_fraud'].iloc[0]
    print(f"  Billing/shipping match: {fraud_sample['billing_shipping_match']}")
    print(f"  CVV result: {fraud_sample['cvv_check_result']}")
    print(f"  AVS result: {fraud_sample['avs_result']}")
    print(f"  High risk category: {fraud_sample['high_risk_category']}")

    # Statistical summary
    print("\n--- Statistical Summary ---")
    print("\nOrder amount by abuse type:")
    print(df.groupby('abuse_type')['order_amount'].describe()[['mean', 'std', 'min', 'max']])

    print("\nAccount age by abuse type:")
    print(df.groupby('abuse_type')['account_age_days'].describe()[['mean', 'std', 'min', 'max']])

    print("\n" + "="*60)


def main():
    """Main entry point for dataset generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic ecommerce abuse detection dataset"
    )
    parser.add_argument(
        '--size',
        type=int,
        default=50000,
        help="Number of records to generate (default: 50000)"
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help="Output CSV file path (default: abuse_dataset_<size>.csv)"
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        '--legitimate-ratio',
        type=float,
        default=0.75,
        help="Proportion of legitimate transactions (default: 0.75)"
    )
    parser.add_argument(
        '--fake-account-ratio',
        type=float,
        default=0.10,
        help="Proportion of fake account abuse (default: 0.10)"
    )
    parser.add_argument(
        '--account-takeover-ratio',
        type=float,
        default=0.08,
        help="Proportion of account takeover (default: 0.08)"
    )
    parser.add_argument(
        '--payment-fraud-ratio',
        type=float,
        default=0.07,
        help="Proportion of payment fraud (default: 0.07)"
    )
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help="Skip dataset validation"
    )

    args = parser.parse_args()

    # Set output path
    if args.output is None:
        output_path = Path(f"abuse_dataset_{args.size}.csv")
    else:
        output_path = Path(args.output)

    print("="*60)
    print("SYNTHETIC ECOMMERCE ABUSE DETECTION DATASET GENERATOR")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  Size: {args.size:,} records")
    print(f"  Output: {output_path}")
    print(f"  Seed: {args.seed}")
    print(f"  Legitimate ratio: {args.legitimate_ratio}")
    print(f"  Fake account ratio: {args.fake_account_ratio}")
    print(f"  Account takeover ratio: {args.account_takeover_ratio}")
    print(f"  Payment fraud ratio: {args.payment_fraud_ratio}")
    print()

    # Generate dataset
    df = generate_dataset(
        size=args.size,
        legitimate_ratio=args.legitimate_ratio,
        fake_account_ratio=args.fake_account_ratio,
        account_takeover_ratio=args.account_takeover_ratio,
        payment_fraud_ratio=args.payment_fraud_ratio,
        seed=args.seed,
    )

    # Validate dataset
    if not args.no_validate:
        validate_dataset(df)

    # Save to CSV
    print(f"\nSaving dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"✓ Dataset saved successfully")

    # Print file info
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\nFile size: {file_size_mb:.2f} MB")
    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
