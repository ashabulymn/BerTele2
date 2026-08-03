from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class N8NConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="N8N_",
        env_file=".env",
        extra="ignore",
    )

    enabled: bool = True
    base_url: str = "http://localhost:5678"
    webhook_path: str = "/webhook"
    api_key: str | None = None
    bearer_token: str | None = None
    timeout_seconds: float = Field(default=15.0, ge=1.0)
    max_retries: int = Field(default=3, ge=0)
    backoff_factor: float = Field(default=1.5, gt=0)
    max_backoff: float = Field(default=30.0, gt=0)
    use_mock_transport: bool = True

    @property
    def api_base_url(self) -> str:
        return self.base_url.rstrip("/")

    @property
    def default_webhook_url(self) -> str:
        path = self.webhook_path.strip()
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.api_base_url}{path}"
