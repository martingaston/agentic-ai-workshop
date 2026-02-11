"""HTTP client for the ML fraud detection service."""

import httpx
from typing import Optional
import logging

from api.models import TransactionRequest, FraudPredictionResponse

logger = logging.getLogger(__name__)


class MLServiceClient:
    """Async HTTP client to communicate with the ML fraud detection service.

    Attributes:
        base_url: Base URL of the ML service (default: http://localhost:8000)
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 10.0
    ):
        """Initialize the ML service client.

        Args:
            base_url: Base URL of the ML service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.predict_url = f"{self.base_url}/api/v1/predict"
        self.health_url = f"{self.base_url}/api/v1/health"

    async def predict(
        self,
        transaction: TransactionRequest
    ) -> FraudPredictionResponse:
        """Get fraud prediction from the ML service.

        Args:
            transaction: Transaction data to analyze

        Returns:
            Fraud prediction with legitimacy score

        Raises:
            httpx.HTTPError: If the request fails
        """
        async with httpx.AsyncClient() as client:
            try:
                logger.debug(
                    f"Sending prediction request for transaction {transaction.transaction_id}"
                )

                response = await client.post(
                    self.predict_url,
                    json=transaction.model_dump(mode='json'),
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()
                prediction = FraudPredictionResponse(**data)

                logger.info(
                    f"Received prediction for {transaction.transaction_id}: "
                    f"score={prediction.legitimacy_score:.3f}"
                )

                return prediction

            except httpx.TimeoutException as e:
                logger.error(f"Timeout calling ML service: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error from ML service: {e.response.status_code} - {e.response.text}"
                )
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling ML service: {e}")
                raise

    async def health_check(self) -> bool:
        """Check if the ML service is available and healthy.

        Returns:
            True if the service is healthy, False otherwise
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.health_url,
                    timeout=5.0
                )
                response.raise_for_status()

                data = response.json()
                is_healthy = data.get("status") == "healthy"

                logger.info(f"ML service health check: {'healthy' if is_healthy else 'unhealthy'}")
                return is_healthy

            except Exception as e:
                logger.warning(f"ML service health check failed: {e}")
                return False
