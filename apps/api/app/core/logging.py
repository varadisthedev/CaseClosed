import logging
import sys

import structlog

from app.core.context import (
    get_case_id,
    get_request_id,
    new_request_id,
    set_request_id,
)


def _add_context(_logger, _method, event_dict):
    request_id = event_dict.get("request_id") or get_request_id()
    case_id = event_dict.get("case_id") or get_case_id()
    if request_id:
        event_dict["request_id"] = request_id
    if case_id:
        event_dict["case_id"] = case_id
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_context,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)


__all__ = [
    "configure_logging",
    "get_logger",
    "new_request_id",
    "set_request_id",
    "get_request_id",
]