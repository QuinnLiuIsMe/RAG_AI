from app.agents.agent import build_agent
from app.core.config import Settings
from app.providers.base import LLMProvider


class TongyiLLMProvider(LLMProvider):
    name = "tongyi"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._agent = None

    def _get_agent(self):
        if self._agent is None:
            self._agent = build_agent(
                model=self._settings.llm_model,
                temperature=self._settings.llm_temperature,
            )
        return self._agent

    def ask(self, question: str) -> str:
        result = self._get_agent().invoke({"input": question})
        return str(result.get("output", "")).strip()

    def readiness(self) -> tuple[bool, str | None]:
        if self._settings.dashscope_api_key:
            return True, None
        return False, "missing APP_DASHSCOPE_API_KEY"
