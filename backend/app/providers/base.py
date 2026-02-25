from typing import Protocol


class LLMProvider(Protocol):
    name: str

    def ask(self, question: str) -> str:
        ...

    def readiness(self) -> tuple[bool, str | None]:
        ...
