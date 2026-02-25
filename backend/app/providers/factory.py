from app.core.config import Settings
from app.providers.base import LLMProvider
from app.providers.mock import MockLLMProvider
from app.providers.tongyi import TongyiLLMProvider


def get_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "tongyi":
        return TongyiLLMProvider(settings)
    return MockLLMProvider()
