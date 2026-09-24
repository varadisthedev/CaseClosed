from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    code: str
    detail: dict = {}
    request_id: str | None = None