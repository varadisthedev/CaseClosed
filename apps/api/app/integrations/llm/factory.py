from app.core.config import Settings, get_settings
from app.integrations.llm.openai_compatible import OpenAiCompatibleClient
from app.integrations.llm.placeholder import PlaceholderLLMClient


def get_llm_client(
    settings: Settings | None = None,
) -> PlaceholderLLMClient | OpenAiCompatibleClient:
    """Select the LLM client by config.

    # PLACEHOLDER(integration-selection): switch LLM_BACKEND=placeholder|openai_compatible
    """
    settings = settings or get_settings()
    if settings.LLM_BACKEND == "openai_compatible":
        return OpenAiCompatibleClient(
            base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY
        )
    return PlaceholderLLMClient()