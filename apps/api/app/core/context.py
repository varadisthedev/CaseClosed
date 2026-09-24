import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
case_id_var: ContextVar[str | None] = ContextVar("case_id", default=None)


def new_request_id() -> str:
    return uuid.uuid4().hex


def set_request_id(value: str | None) -> None:
    request_id_var.set(value)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_case_id(value: str | None) -> None:
    case_id_var.set(value)


def get_case_id() -> str | None:
    return case_id_var.get()