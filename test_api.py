#!/usr/bin/env python3
"""
Load testing script for fraud detection API.

Sends mixed legitimate and fraudulent transactions to the API
and displays results in real-time with color-coded output.
"""
import argparse
import asyncio
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import httpx
import pandas as pd


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class APILoadTester:
    """Load tester for fraud detection API."""

    def __init__(
        self,
        api_url: str,
        rate: float,
        fraud_ratio: float,
        dataset_path: Path
    ) -> None:
        """
        Initialize the load tester.

        Args:
            api_url: Base URL of the API
            rate: Requests per second
            fraud_ratio: Ratio of fraudulent transactions (0.0-1.0)
            dataset_path: Path to the CSV dataset
        """
        self.api_url = api_url
        self.predict_url = f"{api_url}/api/v1/review"
        self.rate = rate
        self.fraud_ratio = fraud_ratio
        self.dataset_path = dataset_path

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        self.legit_scores: List[float] = []
        self.fraud_scores: List[float] = []

        # Data
        self.legitimate_transactions: List[Dict[str, Any]] = []
        self.fraudulent_transactions: List[Dict[str, Any]] = []

        # Graceful shutdown flag
        self.shutdown = False

    def load_transactions(self) -> None:
        """Load and separate transactions from the dataset."""
        print(f"{Colors.CYAN}Loading transactions from {self.dataset_path}...{Colors.RESET}")

        df = pd.read_csv(self.dataset_path)

        # Separate legitimate and fraudulent transactions
        legit_df = df[~df['is_abuse']].copy()
        fraud_df = df[df['is_abuse']].copy()

        print(f"  Loaded {len(legit_df):,} legitimate transactions")
        print(f"  Loaded {len(fraud_df):,} fraudulent transactions")

        # Convert to list of dicts, excluding target columns
        exclude_cols = ['is_abuse', 'abuse_type', 'abuse_confidence', 'difficulty_tier']

        for _, row in legit_df.iterrows():
            transaction = row.drop(exclude_cols).to_dict()
            # Convert datetime strings to ISO 8601 format
            if 'timestamp' in transaction:
                transaction['timestamp'] = str(transaction['timestamp']).replace(' ', 'T')
            if 'account_created_date' in transaction:
                transaction['account_created_date'] = str(transaction['account_created_date']).replace(' ', 'T')
            # Convert card_bin to string (API expects string, pandas reads as int)
            if 'card_bin' in transaction:
                transaction['card_bin'] = str(transaction['card_bin'])
            self.legitimate_transactions.append(transaction)

        for _, row in fraud_df.iterrows():
            transaction = row.drop(exclude_cols).to_dict()
            # Convert datetime strings to ISO 8601 format
            if 'timestamp' in transaction:
                transaction['timestamp'] = str(transaction['timestamp']).replace(' ', 'T')
            if 'account_created_date' in transaction:
                transaction['account_created_date'] = str(transaction['account_created_date']).replace(' ', 'T')
            # Convert card_bin to string (API expects string, pandas reads as int)
            if 'card_bin' in transaction:
                transaction['card_bin'] = str(transaction['card_bin'])
            self.fraudulent_transactions.append(transaction)

        print(f"{Colors.GREEN}✓ Transactions loaded successfully{Colors.RESET}\n")

    async def send_request(
        self,
        client: httpx.AsyncClient,
        transaction: Dict[str, Any],
        is_fraud: bool
    ) -> None:
        """
        Send a single prediction request to the API.

        Args:
            client: Async HTTP client
            transaction: Transaction data
            is_fraud: Whether this is a fraudulent transaction
        """
        self.total_requests += 1
        request_num = self.total_requests

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        transaction_id = transaction.get('transaction_id', f'txn_{request_num}')

        try:
            start_time = time.time()
            response = await client.post(self.predict_url, json=transaction, timeout=10.0)
            elapsed_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result = response.json()
                legitimacy_score = result['legitimacy_score']
                decision = result['decision']

                # Track scores
                if is_fraud:
                    self.fraud_scores.append(legitimacy_score)
                else:
                    self.legit_scores.append(legitimacy_score)

                # Color code based on correctness
                expected = 'FRAUD' if is_fraud else 'LEGIT'
                # Map decision to FRAUD/LEGIT: deny=FRAUD, approve=LEGIT, review=depends on score
                if decision == 'deny':
                    predicted = 'FRAUD'
                elif decision == 'approve':
                    predicted = 'LEGIT'
                else:  # review
                    predicted = 'REVIEW'

                if expected == predicted:
                    status_icon = f"{Colors.GREEN}✓{Colors.RESET}"
                    score_color = Colors.GREEN
                else:
                    status_icon = f"{Colors.RED}✗{Colors.RESET}"
                    score_color = Colors.RED

                print(
                    f"[{timestamp}] {status_icon} {transaction_id[:12]:12s} | "
                    f"Expected: {expected:5s} | Predicted: {predicted:5s} | "
                    f"Score: {score_color}{legitimacy_score:.3f}{Colors.RESET} | "
                    f"{elapsed_ms}ms"
                )

                self.successful_requests += 1
                self.total_response_time += elapsed_ms

            else:
                error_detail = response.text
                print(
                    f"[{timestamp}] {Colors.RED}✗{Colors.RESET} {transaction_id[:12]:12s} | "
                    f"HTTP {response.status_code}"
                )
                if response.status_code == 422:
                    print(f"{Colors.YELLOW}Validation error details:{Colors.RESET}")
                    print(error_detail)
                else:
                    print(f"Error: {error_detail[:200]}")
                self.failed_requests += 1

        except httpx.TimeoutException:
            print(
                f"[{timestamp}] {Colors.RED}✗{Colors.RESET} {transaction_id[:12]:12s} | "
                f"Connection timeout"
            )
            self.failed_requests += 1

        except Exception as e:
            print(
                f"[{timestamp}] {Colors.RED}✗{Colors.RESET} {transaction_id[:12]:12s} | "
                f"Error: {str(e)[:50]}"
            )
            self.failed_requests += 1

    async def run(self) -> None:
        """Run the load test."""
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Fraud Detection API Load Tester{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"API URL: {self.api_url}")
        print(f"Request rate: {self.rate} req/sec")
        print(f"Fraud ratio: {self.fraud_ratio * 100:.0f}%")
        print(f"Press Ctrl+C to stop\n")

        # Load transactions
        self.load_transactions()

        # Check API health
        try:
            async with httpx.AsyncClient() as client:
                health_response = await client.get(f"{self.api_url}/api/v1/health", timeout=5.0)
                if health_response.status_code == 200:
                    health = health_response.json()
                    if health['status'] == 'healthy':
                        print(f"{Colors.GREEN}✓ API is healthy and ready{Colors.RESET}\n")
                    else:
                        print(f"{Colors.RED}✗ API is unhealthy{Colors.RESET}\n")
                        return
                else:
                    print(f"{Colors.RED}✗ API health check failed{Colors.RESET}\n")
                    return
        except Exception as e:
            print(f"{Colors.RED}✗ Cannot connect to API: {e}{Colors.RESET}\n")
            return

        print(f"{Colors.BOLD}Starting load test...{Colors.RESET}\n")

        # Calculate delay between requests
        delay = 1.0 / self.rate if self.rate > 0 else 1.0

        # Transaction indices
        legit_idx = 0
        fraud_idx = 0

        async with httpx.AsyncClient() as client:
            while not self.shutdown:
                # Determine if this should be a fraudulent transaction
                is_fraud = (self.total_requests * self.fraud_ratio) > len(self.fraud_scores)

                if is_fraud and self.fraudulent_transactions:
                    transaction = self.fraudulent_transactions[fraud_idx % len(self.fraudulent_transactions)]
                    fraud_idx += 1
                elif self.legitimate_transactions:
                    transaction = self.legitimate_transactions[legit_idx % len(self.legitimate_transactions)]
                    legit_idx += 1
                else:
                    print("No more transactions to send")
                    break

                # Send request
                await self.send_request(client, transaction, is_fraud)

                # Wait before next request
                await asyncio.sleep(delay)

    def print_statistics(self) -> None:
        """Print summary statistics."""
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Summary Statistics{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"Total requests: {self.total_requests}")
        print(f"Successful: {Colors.GREEN}{self.successful_requests}{Colors.RESET}")
        print(f"Errors: {Colors.RED}{self.failed_requests}{Colors.RESET}")

        if self.successful_requests > 0:
            avg_response_time = self.total_response_time / self.successful_requests
            print(f"Avg response time: {avg_response_time:.1f}ms")

        if self.legit_scores:
            avg_legit_score = sum(self.legit_scores) / len(self.legit_scores)
            print(f"Avg legitimacy score (legit txns): {Colors.GREEN}{avg_legit_score:.3f}{Colors.RESET}")

        if self.fraud_scores:
            avg_fraud_score = sum(self.fraud_scores) / len(self.fraud_scores)
            print(f"Avg legitimacy score (fraud txns): {Colors.RED}{avg_fraud_score:.3f}{Colors.RESET}")

        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def signal_handler(signum, frame):
    """Handle interrupt signal for graceful shutdown."""
    print(f"\n\n{Colors.YELLOW}Received interrupt signal, shutting down...{Colors.RESET}")
    sys.exit(0)


def main():
    """Main entry point."""
    # Force line-buffered output for real-time display when piping to tee
    sys.stdout.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(
        description='Load test the fraud detection API'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:8001',
        help='API base URL (default: http://localhost:8001)'
    )
    parser.add_argument(
        '--rate',
        type=float,
        default=1.0,
        help='Requests per second (default: 1.0)'
    )
    parser.add_argument(
        '--fraud-ratio',
        type=float,
        default=0.5,
        help='Ratio of fraudulent transactions 0.0-1.0 (default: 0.5)'
    )
    parser.add_argument(
        '--dataset',
        default='abuse_dataset_5000_v2.csv',
        help='Path to dataset CSV (default: abuse_dataset_5000_v2.csv)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.rate <= 0:
        print(f"{Colors.RED}Error: Rate must be positive{Colors.RESET}")
        sys.exit(1)

    if not 0 <= args.fraud_ratio <= 1:
        print(f"{Colors.RED}Error: Fraud ratio must be between 0.0 and 1.0{Colors.RESET}")
        sys.exit(1)

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"{Colors.RED}Error: Dataset not found at {dataset_path}{Colors.RESET}")
        sys.exit(1)

    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and run load tester
    tester = APILoadTester(
        api_url=args.api_url,
        rate=args.rate,
        fraud_ratio=args.fraud_ratio,
        dataset_path=dataset_path
    )

    try:
        asyncio.run(tester.run())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Load test interrupted{Colors.RESET}")
    finally:
        tester.print_statistics()


if __name__ == '__main__':
    main()
