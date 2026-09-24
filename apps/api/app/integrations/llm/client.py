from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Contract for LLM providers (AGENTS.md section 17).

    The LLM reasons over retrieved evidence only; it must never invent facts.
    ``response_schema`` is optional structured-output guidance.
    """

    def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: Any = None,
        temperature: float = 0.0,
    ) -> str: ...

    @property
    def source(self) -> str:
        """Either ``llm`` (real) or ``placeholder``."""
        ...