"""Configuration settings for the agent service."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Agent service configuration settings.

    Settings can be overridden via environment variables or .env file.
    """

    # Service configuration
    agent_service_port: int = 8001
    ml_service_url: str = "http://localhost:8000"

    # Decision thresholds
    auto_approve_threshold: float = 0.7
    auto_deny_threshold: float = 0.4

    # LLM configuration (for workshop)
    openai_api_key: str = ""
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.0

    class Config:
        """Pydantic config for settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
