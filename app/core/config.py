from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BERTELE2_",
        extra="ignore",
    )

    app_name: str = "BerTele2"
    version: str = "0.1.0"
    env: str = "production"
    debug: bool = False
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./bertele2.db"
    request_timeout: float = 30.0
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    jwt_secret_key: str = "bertele2-dev-secret"
    jwt_algorithm: str = "HS256"
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    telegram_api_id: int | None = None
    telegram_api_hash: str | None = None
    telegram_session_string: str | None = None
    telegram_phone_number: str | None = None
    telegram_bot_token: str | None = None
    telegram_media_max_download_size: int = Field(default=50 * 1024 * 1024)
    telegram_media_chunk_size: int = Field(default=1024 * 1024)
    telegram_media_download_timeout: float = Field(default=30.0)
    telegram_media_retry_count: int = Field(default=3)
    media_provider: str = Field(default="local")
    media_storage_path: str = Field(default="./storage/media")
    media_max_size: int = Field(default=50 * 1024 * 1024)
    media_allowed_extensions: str = Field(
        default=".jpg,.jpeg,.png,.gif,.webp,.mp4,.mov,.mp3,.wav,.ogg,.pdf,.txt,.bin"
    )
    websocket_max_connections: int = Field(default=100)

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def alembic_database_url(self) -> str:
        if self.database_url.startswith("sqlite+aiosqlite"):
            return self.database_url.replace("+aiosqlite", "")
        if self.database_url.startswith("postgresql+asyncpg"):
            return self.database_url.replace("+asyncpg", "")
        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
