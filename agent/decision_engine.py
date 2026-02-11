"""Core decision logic for fraud detection using ML and agent review."""

import logging
from typing import Optional

from api.models import TransactionRequest, FraudPredictionResponse
from agent.models import FraudDecisionResponse
from agent.ml_client import MLServiceClient

logger = logging.getLogger(__name__)


class FraudDecisionEngine:
    """Orchestrates fraud decisions using ML predictions and agent review.

    The engine implements a three-tier decision strategy:
    - Auto-approve: legitimacy_score >= 0.7 (low fraud risk)
    - Auto-deny: legitimacy_score <= 0.4 (high fraud risk)
    - Agent review: 0.4 < legitimacy_score < 0.7 (uncertain cases)

    Attributes:
        ml_client: HTTP client for the ML service
        auto_approve_threshold: Score threshold for auto-approval
        auto_deny_threshold: Score threshold for auto-denial
    """

    def __init__(
        self,
        ml_client: MLServiceClient,
        auto_approve_threshold: float = 0.7,
        auto_deny_threshold: float = 0.4
    ):
        """Initialize the decision engine.

        Args:
            ml_client: Client for communicating with the ML service
            auto_approve_threshold: Minimum score for auto-approval
            auto_deny_threshold: Maximum score for auto-denial
        """
        self.ml_client = ml_client
        self.auto_approve_threshold = auto_approve_threshold
        self.auto_deny_threshold = auto_deny_threshold

        logger.info(
            f"Decision engine initialized with thresholds: "
            f"approve>={auto_approve_threshold}, deny<={auto_deny_threshold}"
        )

    async def make_decision(
        self,
        transaction: TransactionRequest
    ) -> FraudDecisionResponse:
        """Make a fraud decision for the given transaction.

        Decision flow:
        1. Get ML prediction
        2. Apply threshold-based decision rules
        3. For uncertain cases (0.4-0.7), trigger agent review (placeholder)

        Args:
            transaction: Transaction to analyze

        Returns:
            FraudDecisionResponse with decision and reasoning

        Raises:
            Exception: If ML service is unavailable or fails
        """
        logger.info(f"Making decision for transaction {transaction.transaction_id}")

        # Step 1: Get ML prediction
        try:
            ml_prediction = await self.ml_client.predict(transaction)
            score = ml_prediction.legitimacy_score
        except Exception as e:
            logger.error(f"Failed to get ML prediction: {e}")
            raise

        # Step 2: Apply threshold-based decisions
        if score >= self.auto_approve_threshold:
            # Auto-approve: High legitimacy score
            decision = self._auto_approve_decision(
                transaction.transaction_id,
                score,
                ml_prediction
            )
            logger.info(
                f"Auto-approved {transaction.transaction_id} with score {score:.3f}"
            )
            return decision

        elif score <= self.auto_deny_threshold:
            # Auto-deny: Low legitimacy score
            decision = self._auto_deny_decision(
                transaction.transaction_id,
                score,
                ml_prediction
            )
            logger.info(
                f"Auto-denied {transaction.transaction_id} with score {score:.3f}"
            )
            return decision

        else:
            # Uncertain - trigger agent review (PLACEHOLDER)
            logger.info(
                f"Transaction {transaction.transaction_id} requires agent review "
                f"(score {score:.3f} in uncertain range)"
            )
            return await self._agent_review(transaction, ml_prediction)

    def _auto_approve_decision(
        self,
        transaction_id: str,
        score: float,
        ml_prediction: FraudPredictionResponse
    ) -> FraudDecisionResponse:
        """Create an auto-approve decision.

        Args:
            transaction_id: Transaction identifier
            score: Legitimacy score
            ml_prediction: Raw ML prediction data

        Returns:
            FraudDecisionResponse with approve decision
        """
        return FraudDecisionResponse(
            transaction_id=transaction_id,
            decision="approve",
            legitimacy_score=score,
            decision_maker="ml_model",
            reasoning=(
                f"Auto-approved: High legitimacy score ({score:.3f}). "
                f"The ML model indicates this transaction has low fraud risk."
            ),
            ml_prediction=ml_prediction.model_dump()
        )

    def _auto_deny_decision(
        self,
        transaction_id: str,
        score: float,
        ml_prediction: FraudPredictionResponse
    ) -> FraudDecisionResponse:
        """Create an auto-deny decision.

        Args:
            transaction_id: Transaction identifier
            score: Legitimacy score
            ml_prediction: Raw ML prediction data

        Returns:
            FraudDecisionResponse with deny decision
        """
        return FraudDecisionResponse(
            transaction_id=transaction_id,
            decision="deny",
            legitimacy_score=score,
            decision_maker="ml_model",
            reasoning=(
                f"Auto-denied: Low legitimacy score ({score:.3f}). "
                f"The ML model indicates this transaction has high fraud risk."
            ),
            ml_prediction=ml_prediction.model_dump()
        )

    async def _agent_review(
        self,
        transaction: TransactionRequest,
        ml_prediction: FraudPredictionResponse
    ) -> FraudDecisionResponse:
        """Trigger agent review for uncertain transactions.

        PLACEHOLDER: This method returns a placeholder response for workshop implementation.

        Workshop participants will implement:
        1. Invoke the langchain agent with fraud review tools
        2. Analyze transaction attributes (account age, verification status, etc.)
        3. Apply reasoning to make an informed decision
        4. Return approve/deny decision with agent analysis

        Args:
            transaction: Transaction to review
            ml_prediction: ML prediction data

        Returns:
            FraudDecisionResponse with review_required status (placeholder)
        """
        # PLACEHOLDER - for workshop implementation
        logger.warning(
            f"Agent review not yet implemented for transaction {transaction.transaction_id}"
        )

        # WORKSHOP TODO: Implement agent review logic
        # 1. Create agent context with transaction data and ML prediction
        # 2. Invoke langchain agent with fraud_review_tool
        # 3. Parse agent's decision and reasoning
        # 4. Return FraudDecisionResponse with decision="approve" or "deny"
        #    and decision_maker="agent"

        agent_analysis = (
            "PLACEHOLDER: Agent review not yet implemented.\n\n"
            "WORKSHOP TODO: Implement agent logic to analyze:\n"
            f"- Account age ({transaction.account_age_days} days) vs order amount (${transaction.order_amount:.2f})\n"
            f"- Failed login attempts ({transaction.failed_login_attempts_24h})\n"
            f"- Email verified: {transaction.email_verified}, Phone verified: {transaction.phone_verified}\n"
            f"- New device: {transaction.new_device}, VPN/Proxy: {transaction.vpn_proxy_detected}\n"
            f"- Billing/shipping match: {transaction.billing_shipping_match}\n"
            f"- Payment verification: CVV={transaction.cvv_check_result}, AVS={transaction.avs_result}\n"
            f"- Orders in last 24h: {transaction.orders_last_24h}\n"
            "\n"
            "The agent should reason about these factors and make a decision."
        )

        return FraudDecisionResponse(
            transaction_id=transaction.transaction_id,
            decision="review",
            legitimacy_score=ml_prediction.legitimacy_score,
            decision_maker="review_required",
            reasoning=(
                f"Uncertain case: legitimacy score ({ml_prediction.legitimacy_score:.3f}) "
                f"falls in the uncertain range ({self.auto_deny_threshold}-{self.auto_approve_threshold}). "
                "Agent review logic needs to be implemented."
            ),
            ml_prediction=ml_prediction.model_dump(),
            agent_analysis=agent_analysis
        )
