#!/usr/bin/env python
"""
Agent Service Tester - Workshop Tool

Generates synthetic transactions and tests the agent service.
Displays results categorized by decision type.

Usage:
    uv run python agent/test_agent.py --num-transactions 50 --fraud-ratio 0.5
    uv run python agent/test_agent.py --num-transactions 100 --fraud-ratio 0.3 --show-details
"""

import asyncio
import httpx
import argparse
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime
import json

# Import from existing modules
from data.generate_synthetic_data import generate_dataset
from schema import TransactionRecord


class AgentTester:
    """Tests the agent service with synthetic transaction data."""

    def __init__(self, agent_url: str = "http://localhost:8001"):
        """Initialize the tester.

        Args:
            agent_url: Base URL of the agent service
        """
        self.agent_url = agent_url
        self.review_url = f"{agent_url}/api/v1/review"
        self.results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def test_transaction(
        self,
        transaction: TransactionRecord,
        client: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Send a single transaction to the agent service.

        Args:
            transaction: Transaction record to test
            client: HTTP client

        Returns:
            Dict with transaction, decision, success flag, and error (if any)
        """
        try:
            response = await client.post(
                self.review_url,
                json=transaction.to_dict(),
                timeout=30.0
            )
            response.raise_for_status()
            decision_data = response.json()

            return {
                "transaction": transaction,
                "decision": decision_data,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "transaction": transaction,
                "decision": None,
                "success": False,
                "error": str(e)
            }

    async def run_tests(
        self,
        num_transactions: int,
        fraud_ratio: float
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate transactions and test them against the agent service.

        Args:
            num_transactions: Number of transactions to generate
            fraud_ratio: Ratio of fraudulent transactions (0.0-1.0)

        Returns:
            Dict categorizing results by decision type
        """
        print(f"\n{'='*70}")
        print(f"Agent Service Test Runner")
        print(f"{'='*70}")
        print(f"Generating {num_transactions} synthetic transactions...")
        print(f"Fraud ratio: {fraud_ratio:.1%}")
        print(f"Agent URL: {self.agent_url}")
        print(f"{'='*70}\n")

        # Generate synthetic data
        # Split fraud_ratio among different fraud types
        legitimate_ratio = 1.0 - fraud_ratio
        fake_account_ratio = fraud_ratio * 0.4
        account_takeover_ratio = fraud_ratio * 0.3
        payment_fraud_ratio = fraud_ratio * 0.3

        df = generate_dataset(
            size=num_transactions,
            legitimate_ratio=legitimate_ratio,
            suspicious_but_legitimate_ratio=0.0,  # Keep it simple
            fake_account_ratio=fake_account_ratio,
            account_takeover_ratio=account_takeover_ratio,
            payment_fraud_ratio=payment_fraud_ratio
        )

        # Convert DataFrame rows back to TransactionRecord objects
        transactions = []
        for _, row in df.iterrows():
            # Convert datetime strings back to datetime objects if needed
            row_dict = row.to_dict()
            if isinstance(row_dict['timestamp'], str):
                from datetime import datetime
                row_dict['timestamp'] = datetime.strptime(row_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
                row_dict['account_created_date'] = datetime.strptime(row_dict['account_created_date'], '%Y-%m-%d %H:%M:%S')
            transactions.append(TransactionRecord(**row_dict))

        # Test all transactions
        async with httpx.AsyncClient() as client:
            tasks = [
                self.test_transaction(tx, client)
                for tx in transactions
            ]
            results = await asyncio.gather(*tasks)

        # Categorize results
        for result in results:
            if not result["success"]:
                self.results["errors"].append(result)
            else:
                decision = result["decision"]["decision"]
                self.results[decision].append(result)

        return self.results

    def print_summary(self, show_details: bool = False):
        """Print summary of test results.

        Args:
            show_details: Whether to show detailed sample transactions
        """
        print(f"\n{'='*70}")
        print(f"TEST RESULTS SUMMARY")
        print(f"{'='*70}\n")

        total = sum(len(results) for results in self.results.values())

        # Overall statistics
        print(f"Total transactions tested: {total}")
        print(f"  ✅ Approved: {len(self.results['approve'])}")
        print(f"  ❌ Denied: {len(self.results['deny'])}")
        print(f"  🔍 Needs Review: {len(self.results['review'])}")
        print(f"  ⚠️  Errors: {len(self.results['errors'])}\n")

        # Decision breakdown by score range
        if self.results['approve']:
            scores = [r['decision']['legitimacy_score'] for r in self.results['approve']]
            print(f"Approved transactions (n={len(scores)}):")
            print(f"  Score range: {min(scores):.3f} - {max(scores):.3f}")
            print(f"  Average score: {sum(scores)/len(scores):.3f}\n")

        if self.results['deny']:
            scores = [r['decision']['legitimacy_score'] for r in self.results['deny']]
            print(f"Denied transactions (n={len(scores)}):")
            print(f"  Score range: {min(scores):.3f} - {max(scores):.3f}")
            print(f"  Average score: {sum(scores)/len(scores):.3f}\n")

        if self.results['review']:
            scores = [r['decision']['legitimacy_score'] for r in self.results['review']]
            print(f"Review required transactions (n={len(scores)}):")
            print(f"  Score range: {min(scores):.3f} - {max(scores):.3f}")
            print(f"  Average score: {sum(scores)/len(scores):.3f}")
            print(f"  📝 Workshop Task: Implement agent logic for these!\n")

        # Show sample details if requested
        if show_details:
            self._print_detailed_samples()

        print(f"{'='*70}\n")

    def _print_detailed_samples(self):
        """Print detailed information for sample transactions."""
        print(f"\n{'='*70}")
        print(f"SAMPLE TRANSACTION DETAILS")
        print(f"{'='*70}\n")

        # Show one sample from each category
        for decision_type in ['approve', 'deny', 'review']:
            if self.results[decision_type]:
                result = self.results[decision_type][0]
                tx = result['transaction']
                decision = result['decision']

                print(f"\n{decision_type.upper()} Sample:")
                print(f"  Transaction ID: {tx.transaction_id}")
                print(f"  Legitimacy Score: {decision['legitimacy_score']:.3f}")
                print(f"  Decision Maker: {decision['decision_maker']}")
                print(f"  Reasoning: {decision['reasoning']}")
                print(f"\n  Key Transaction Attributes:")
                print(f"    Account age: {tx.account_age_days} days")
                print(f"    Order amount: ${tx.order_amount:.2f}")
                print(f"    Email verified: {tx.email_verified}")
                print(f"    Phone verified: {tx.phone_verified}")
                print(f"    New device: {tx.new_device}")
                print(f"    Billing/Shipping match: {tx.billing_shipping_match}")
                print(f"    Payment verification: CVV={tx.cvv_check_result}, AVS={tx.avs_result}")
                print(f"    Failed logins (24h): {tx.failed_login_attempts_24h}")
                print(f"    VPN/Proxy detected: {tx.vpn_proxy_detected}")

        if self.results['errors']:
            print(f"\nERROR Sample:")
            error = self.results['errors'][0]
            print(f"  Transaction ID: {error['transaction'].transaction_id}")
            print(f"  Error: {error['error']}")

    def export_review_cases(self, output_file: str = "review_cases.json"):
        """Export transactions needing review for workshop analysis.

        Args:
            output_file: Path to output JSON file
        """
        review_cases = [
            {
                "transaction_id": r['transaction'].transaction_id,
                "legitimacy_score": r['decision']['legitimacy_score'],
                "transaction_data": r['transaction'].to_dict(),
                "decision_data": r['decision']
            }
            for r in self.results['review']
        ]

        with open(output_file, 'w') as f:
            json.dump(review_cases, f, indent=2, default=str)

        print(f"\n📁 Exported {len(review_cases)} review cases to {output_file}")


async def main():
    """Main entry point for the tester."""
    parser = argparse.ArgumentParser(
        description="Test the agent service with synthetic transactions"
    )
    parser.add_argument(
        "--num-transactions",
        type=int,
        default=50,
        help="Number of transactions to generate (default: 50)"
    )
    parser.add_argument(
        "--fraud-ratio",
        type=float,
        default=0.5,
        help="Ratio of fraudulent transactions (default: 0.5)"
    )
    parser.add_argument(
        "--agent-url",
        type=str,
        default="http://localhost:8001",
        help="Agent service URL (default: http://localhost:8001)"
    )
    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Show detailed sample transactions"
    )
    parser.add_argument(
        "--export-reviews",
        action="store_true",
        help="Export review cases to JSON file"
    )

    args = parser.parse_args()

    # Run tests
    tester = AgentTester(agent_url=args.agent_url)

    try:
        await tester.run_tests(
            num_transactions=args.num_transactions,
            fraud_ratio=args.fraud_ratio
        )

        # Print results
        tester.print_summary(show_details=args.show_details)

        # Export review cases if requested
        if args.export_reviews:
            tester.export_review_cases()

    except httpx.ConnectError:
        print(f"\n❌ Error: Could not connect to agent service at {args.agent_url}")
        print(f"   Make sure the agent service is running:")
        print(f"   uv run uvicorn agent.main:app --port 8001\n")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
