"""FastAPI application for fraud detection agent service.

This service wraps the ML fraud detection model with intelligent decision-making:
- Auto-approves transactions with legitimacy scores >= 0.7
- Auto-denies transactions with legitimacy scores <= 0.4
- Triggers agent review for uncertain cases (0.4-0.7)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from api.models import TransactionRequest
from agent.models import FraudDecisionResponse, HealthResponse, AgentInfoResponse
from agent.ml_client import MLServiceClient
from agent.decision_engine import FraudDecisionEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service version
SERVICE_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown.

    Lifecycle:
    1. Initialize ML service client
    2. Check ML service availability
    3. Initialize decision engine
    4. Store in app state for endpoint access
    """
    logger.info("Starting fraud detection agent service...")

    # Initialize ML service client
    ml_client = MLServiceClient(base_url="http://localhost:8000")

    # Check ML service availability
    is_healthy = await ml_client.health_check()
    if not is_healthy:
        logger.warning(
            "ML service not available at startup. "
            "The service will continue but predictions will fail until ML service is available."
        )
    else:
        logger.info("ML service is healthy and available")

    # Initialize decision engine
    decision_engine = FraudDecisionEngine(
        ml_client=ml_client,
        auto_approve_threshold=0.7,
        auto_deny_threshold=0.4
    )

    # Store in app state
    app.state.ml_client = ml_client
    app.state.decision_engine = decision_engine
    app.state.auto_approve_threshold = 0.7
    app.state.auto_deny_threshold = 0.4

    logger.info(f"Agent service v{SERVICE_VERSION} started successfully on port 8001")

    yield

    # Cleanup
    logger.info("Agent service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Fraud Detection Agent Service",
    description=(
        "Intelligent fraud detection service using ML predictions and agent-based review. "
        "Auto-approves low-risk transactions, auto-denies high-risk, and triggers agent "
        "review for uncertain cases."
    ),
    version=SERVICE_VERSION,
    lifespan=lifespan
)


@app.get("/", response_model=Dict[str, Any])
async def root() -> Dict[str, Any]:
    """Service information and available endpoints.

    Returns:
        Service metadata with links to endpoints
    """
    return {
        "service": "Fraud Detection Agent Service",
        "version": SERVICE_VERSION,
        "description": "Intelligent fraud detection with ML and agent-based review",
        "endpoints": {
            "health": "/api/v1/health",
            "agent_info": "/api/v1/agent/info",
            "review_transaction": "/api/v1/review"
        },
        "decision_thresholds": {
            "auto_approve": "legitimacy_score >= 0.7",
            "auto_deny": "legitimacy_score <= 0.4",
            "agent_review": "0.4 < legitimacy_score < 0.7"
        }
    }


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint.

    Verifies:
    - Agent service is running
    - ML service is reachable

    Returns:
        HealthResponse with service status
    """
    ml_client: MLServiceClient = request.app.state.ml_client

    # Check ML service health
    ml_healthy = await ml_client.health_check()

    # Overall status
    status = "healthy" if ml_healthy else "degraded"

    return HealthResponse(
        status=status,
        ml_service_available=ml_healthy,
        agent_service_version=SERVICE_VERSION
    )


@app.get("/api/v1/agent/info", response_model=AgentInfoResponse)
async def agent_info(request: Request) -> AgentInfoResponse:
    """Get agent service configuration and status.

    Returns:
        AgentInfoResponse with thresholds and agent status
    """
    auto_approve = request.app.state.auto_approve_threshold
    auto_deny = request.app.state.auto_deny_threshold

    return AgentInfoResponse(
        service_name="Fraud Detection Agent",
        version=SERVICE_VERSION,
        auto_approve_threshold=auto_approve,
        auto_deny_threshold=auto_deny,
        agent_status="placeholder"  # Will change to "active" when agent is implemented
    )


@app.post("/api/v1/review", response_model=FraudDecisionResponse)
async def review_transaction(
    transaction: TransactionRequest,
    request: Request
) -> FraudDecisionResponse:
    """Review transaction and make fraud decision.

    Decision paths:
    - Score >= 0.7: Auto-approve (low fraud risk)
    - Score <= 0.4: Auto-deny (high fraud risk)
    - 0.4 < Score < 0.7: Agent review (uncertain - PLACEHOLDER)

    Args:
        transaction: Transaction data to review

    Returns:
        FraudDecisionResponse with decision, score, and reasoning

    Raises:
        HTTPException: If ML service is unavailable or fails
    """
    logger.info(f"Received review request for transaction {transaction.transaction_id}")
    decision_engine: FraudDecisionEngine = request.app.state.decision_engine

    try:
        # Make decision using the decision engine
        decision = await decision_engine.make_decision(transaction)

        logger.info(
            f"Decision for {transaction.transaction_id}: "
            f"{decision.decision} (by {decision.decision_maker})"
        )

        return decision

    except Exception as e:
        logger.error(f"Error processing transaction {transaction.transaction_id}: {e}", exc_info=True)

        # Return 503 if ML service is unavailable
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service temporarily unavailable",
                "message": f"Unable to process transaction: {str(e)}",
                "transaction_id": transaction.transaction_id
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors.

    Args:
        request: The request that caused the error
        exc: The exception that was raised

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
