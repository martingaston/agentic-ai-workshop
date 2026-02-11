#!/usr/bin/env python3
"""
Test specific transactions that fall in the review zone (0.4-0.7 legitimacy score).
Sends direct API requests to the agent service.
"""
import sys
import httpx
import pandas as pd
from datetime import datetime


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def prepare_transaction(row: pd.Series) -> dict:
    """Convert CSV row to API-compatible transaction dict."""
    # Exclude target columns
    exclude_cols = ['is_abuse', 'abuse_type', 'abuse_confidence', 'difficulty_tier']
    transaction = row.drop(exclude_cols).to_dict()

    # Convert datetime strings to ISO 8601 format
    if 'timestamp' in transaction:
        transaction['timestamp'] = str(transaction['timestamp']).replace(' ', 'T')
    if 'account_created_date' in transaction:
        transaction['account_created_date'] = str(transaction['account_created_date']).replace(' ', 'T')

    # Convert card_bin to string
    if 'card_bin' in transaction:
        transaction['card_bin'] = str(transaction['card_bin'])

    return transaction


def test_transaction(client: httpx.Client, transaction: dict, is_fraud: bool) -> None:
    """Test a single transaction and display results."""
    txn_id = transaction['transaction_id']

    try:
        response = client.post(
            'http://localhost:8081/api/v1/review',
            json=transaction,
            timeout=10.0
        )

        if response.status_code == 200:
            result = response.json()
            score = result['legitimacy_score']
            decision = result['decision']
            decision_maker = result['decision_maker']
            reasoning = result['reasoning']

            # Determine expected vs predicted
            expected = 'FRAUD' if is_fraud else 'LEGIT'
            if decision == 'deny':
                predicted = 'FRAUD'
            elif decision == 'approve':
                predicted = 'LEGIT'
            else:
                predicted = 'REVIEW'

            # Color based on score range
            if 0.4 <= score < 0.7:
                score_color = Colors.YELLOW
                marker = "⚠️ "
            elif score >= 0.7:
                score_color = Colors.GREEN
                marker = "✓ "
            else:
                score_color = Colors.RED
                marker = "✗ "

            print(f"\n{Colors.BOLD}Transaction: {txn_id}{Colors.RESET}")
            print(f"  {marker}Expected: {expected} | Predicted: {predicted}")
            print(f"  Score: {score_color}{score:.3f}{Colors.RESET}")
            print(f"  Decision: {decision.upper()} (by {decision_maker})")
            print(f"  Reasoning: {reasoning}")

        else:
            print(f"\n{Colors.RED}✗ Error testing {txn_id}: HTTP {response.status_code}{Colors.RESET}")
            print(f"  {response.text}")

    except Exception as e:
        print(f"\n{Colors.RED}✗ Error testing {txn_id}: {e}{Colors.RESET}")


def main():
    """Main entry point."""
    # Transaction ID prefixes that had scores in review zone
    target_prefixes = ['TXN_20251115', 'TXN_20251202', 'TXN_20251205', 'TXN_20251211']

    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}Testing Transactions in Review Zone (0.4-0.7){Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")

    # Load dataset
    df = pd.read_csv('abuse_dataset_5000_v2.csv')

    # Find transactions matching the prefixes and are fraudulent
    matching_transactions = []
    for prefix in target_prefixes:
        matches = df[df['transaction_id'].str.startswith(prefix) & df['is_abuse']]
        if not matches.empty:
            # Take first match for each prefix
            matching_transactions.append(matches.iloc[0])

    print(f"\nFound {len(matching_transactions)} transactions to test")
    print(f"{Colors.CYAN}Testing against: http://localhost:8081/api/v1/review{Colors.RESET}\n")

    # Test each transaction
    with httpx.Client() as client:
        for row in matching_transactions:
            transaction = prepare_transaction(row)
            is_fraud = row['is_abuse']
            test_transaction(client, transaction, is_fraud)

    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}Testing Complete{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")


if __name__ == '__main__':
    main()
