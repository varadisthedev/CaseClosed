from app.core.config import Settings, get_settings
from app.integrations.mcp.graph_client import McpGraphClient
from app.integrations.tigergraph.placeholder import PlaceholderGraphClient


def get_graph_client(settings: Settings | None = None) -> PlaceholderGraphClient | McpGraphClient:
    """Select the graph client by config.

    # PLACEHOLDER(integration-selection): switch GRAPH_BACKEND=placeholder|mcp
    """
    settings = settings or get_settings()
    if settings.GRAPH_BACKEND == "mcp":
        return McpGraphClient()
    return PlaceholderGraphClient()