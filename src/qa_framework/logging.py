"""Structured logging configuration with structlog."""

import logging
import sys
from datetime import UTC
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

from .config import get_settings


def add_log_level(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def add_timestamp(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add ISO timestamp to event dict."""
    from datetime import datetime

    event_dict["timestamp"] = datetime.now(UTC).isoformat()
    return event_dict


def drop_color_message_key(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Remove color_message key if present."""
    event_dict.pop("color_message", None)
    return event_dict


def configure_logging() -> None:
    """Configure structlog for the application."""
    settings = get_settings()

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        add_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        drop_color_message_key,
    ]

    if settings.env == "local":
        # Pretty console output for local development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON output for CI/production
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
    )

    # Quiet noisy loggers
    for logger_name in ["httpx", "httpcore", "playwright", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)  # type: ignore


class LogContext:
    """Context manager for adding contextual information to logs."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.tokens: list[dict[str, Any]] = []

    def __enter__(self) -> "LogContext":
        token = structlog.contextvars.bind_contextvars(**self.kwargs)
        self.tokens.append(dict(token))  # Convert Mapping to dict
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        for token in self.tokens:
            keys = list(token.keys())
            structlog.contextvars.unbind_contextvars(*keys)


# Initialize on import
configure_logging()
