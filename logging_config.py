"""
Structured logging configuration using structlog.
Provides JSON logs for production and pretty logs for development.
"""
import structlog
import logging
import sys
from typing import Any

def configure_logging(json_logs: bool = True) -> None:
    """
    Configure structlog for the application.
    
    Args:
        json_logs: If True, output JSON format (production).
                   If False, output human-readable format (development).
    """
    # Shared processors for all configurations
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        # Production: JSON formatted logs
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Pretty colored logs
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str = __name__) -> Any:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__ from calling module)
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)
