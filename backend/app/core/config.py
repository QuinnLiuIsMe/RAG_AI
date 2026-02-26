from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Ops Agent"
    app_env: Literal["dev", "test", "prod"] = "dev"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    llm_provider: Literal["mock", "tongyi"] = "mock"
    llm_model: str = "qwen-max"
    llm_temperature: float = 0.0
    dashscope_api_key: str | None = None

    auth_enabled: bool = False
    auth_issuer: str | None = None
    auth_audience: str | None = None
    auth_verify_signature: bool = False
    auth_hs256_secret: str | None = None

    rate_limit_per_minute: int = 60

    guardrail_max_input_chars: int = 6000
    guardrail_blocked_phrases: str = "<script>,drop table,ignore previous instructions,begin rsa private key"

    cache_backend: Literal["memory", "redis"] = "memory"
    cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
