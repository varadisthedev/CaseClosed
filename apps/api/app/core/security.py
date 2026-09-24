from fastapi import Header

from app.core.config import get_settings
from app.core.errors import UnauthorizedError

API_KEY_HEADER = "X-API-Key"


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Minimal API-key gate.

    Disabled (no-op) when ``API_KEY`` is unset, so local/demo usage needs no
    credentials. When set, requests must present a matching ``X-API-Key``.
    """
    settings = get_settings()
    if not settings.API_KEY:
        return
    if x_api_key != settings.API_KEY:
        raise UnauthorizedError("Invalid or missing API key")