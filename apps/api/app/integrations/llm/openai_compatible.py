from typing import Any


class OpenAiCompatibleClient:
    """Skeleton for a real OpenAI-compatible / provider LLM client.

    # PLACEHOLDER(llm-provider): fill this in with the actual provider call
    # (e.g. Gemini via google-genai or an OpenAI-compatible endpoint) using
    # settings LLM_PROVIDER / LLM_MODEL / LLM_API_KEY. Not required to work.
    """

    source = "llm"

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: Any = None,
        temperature: float = 0.0,
    ) -> str:
        raise NotImplementedError(
            "PLACEHOLDER(llm-provider): real LLM provider not wired yet"
        )