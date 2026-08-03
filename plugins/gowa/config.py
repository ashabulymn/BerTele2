from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoWAConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GOWA_",
        env_file=".env",
        extra="ignore",
    )

    enabled: bool = True
    base_url: str = "http://localhost:8080"
    api_key: str | None = None
    webhook_secret: str | None = None
    timeout_seconds: float = Field(default=15.0, ge=1.0)
    max_retries: int = Field(default=3, ge=0)
    backoff_factor: float = Field(default=1.5, gt=0)
    max_backoff: float = Field(default=30.0, gt=0)
    use_mock_transport: bool = True

    @property
    def api_base_url(self) -> str:
        return self.base_url.rstrip("/")
