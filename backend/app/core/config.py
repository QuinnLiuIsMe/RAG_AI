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

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
