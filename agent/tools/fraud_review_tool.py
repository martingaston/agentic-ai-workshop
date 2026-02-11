"""Langchain tool for analyzing transactions for fraud indicators.

PLACEHOLDER: This is a workshop exercise for attendees to implement.
"""

from langchain.tools import Tool
import json


def placeholder_fraud_review(transaction_data: str) -> str:
    """Analyze transaction for fraud indicators.

    PLACEHOLDER: Workshop participants will implement the actual fraud analysis logic.

    Workshop TODO: Implement analysis logic considering:
    - Account age vs. order value (new accounts with high-value orders are suspicious)
    - Failed login attempts and transaction velocity (rapid attempts suggest credential stuffing)
    - Geographic mismatches (billing/shipping in different countries)
    - Payment verification failures (CVV/AVS mismatches)
    - New device from new location (indicates potential account takeover)
    - Email/phone verification status (unverified accounts are riskier)

    The tool should:
    1. Parse the transaction data JSON
    2. Evaluate each fraud indicator
    3. Assign risk scores to each indicator
    4. Return a structured analysis with reasoning

    Args:
        transaction_data: JSON string containing transaction attributes

    Returns:
        Structured analysis of fraud indicators (currently a placeholder)
    """
    # PLACEHOLDER - for workshop implementation
    try:
        data = json.loads(transaction_data)
        transaction_id = data.get("transaction_id", "unknown")

        placeholder_response = (
            f"PLACEHOLDER: Fraud review tool not yet implemented for transaction {transaction_id}.\n\n"
            "WORKSHOP TODO: Implement fraud indicator analysis.\n\n"
            "Expected analysis framework:\n"
            "1. Account Risk Assessment:\n"
            "   - Account age vs order value ratio\n"
            "   - Historical transaction patterns\n"
            "   - Verification status (email, phone)\n\n"
            "2. Authentication Risk:\n"
            "   - Failed login attempts\n"
            "   - Device fingerprint analysis\n"
            "   - Location analysis\n\n"
            "3. Payment Risk:\n"
            "   - CVV/AVS verification results\n"
            "   - Billing/shipping address matching\n"
            "   - Payment method risk\n\n"
            "4. Behavioral Risk:\n"
            "   - Transaction velocity (24h window)\n"
            "   - New device from new location flag\n"
            "   - Time of day patterns\n\n"
            "Output should be: risk_score (0-100), list of red flags, and recommendation."
        )

        return placeholder_response

    except json.JSONDecodeError:
        return "ERROR: Invalid transaction data format. Expected JSON string."


# Create the langchain Tool
fraud_review_tool = Tool(
    name="analyze_fraud_indicators",
    func=placeholder_fraud_review,
    description=(
        "Analyzes a transaction for fraud indicators and risk factors. "
        "Input should be a JSON string containing transaction attributes including: "
        "transaction_id, account_age_days, order_amount, email_verified, phone_verified, "
        "failed_login_attempts, new_device, new_location, billing_shipping_match, "
        "cvv_check_result, avs_result, transaction_velocity_24h, and other relevant fields. "
        "Returns a structured analysis with risk assessment and recommendations."
    )
)
