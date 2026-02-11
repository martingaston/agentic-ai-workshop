"""Pydantic models for agent service API contracts."""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class FraudDecisionResponse(BaseModel):
    """Enhanced response with decision and decision maker.

    Attributes:
        transaction_id: Unique identifier for the transaction
        decision: Final decision (approve, deny, or review)
        legitimacy_score: ML model's legitimacy score (0.0-1.0)
        decision_maker: Who made the decision (ml_model, agent, or review_required)
        reasoning: Human-readable explanation of the decision
        ml_prediction: Optional raw ML prediction data
        agent_analysis: Optional agent's detailed analysis
    """

    transaction_id: str
    decision: Literal["approve", "deny", "review"]
    legitimacy_score: float = Field(ge=0.0, le=1.0)
    decision_maker: Literal["ml_model", "agent", "review_required"]
    reasoning: str
    ml_prediction: Optional[dict] = None
    agent_analysis: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Overall service status
        ml_service_available: Whether ML service is reachable
        agent_service_version: Version of the agent service
    """

    status: str
    ml_service_available: bool
    agent_service_version: str


class AgentInfoResponse(BaseModel):
    """Agent service configuration information.

    Attributes:
        service_name: Name of the service
        version: Service version
        auto_approve_threshold: Score threshold for auto-approval (>= this value)
        auto_deny_threshold: Score threshold for auto-denial (<= this value)
        agent_status: Current agent status (placeholder/active)
    """

    service_name: str
    version: str
    auto_approve_threshold: float
    auto_deny_threshold: float
    agent_status: str
