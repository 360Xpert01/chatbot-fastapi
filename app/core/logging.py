"""
Structured logging configuration for the application.
Replaces print() statements with proper logging.
"""
import logging
import sys
from typing import Optional


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter with structured format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    return logging.getLogger(name)


# Convenience function for quick logging setup
def init_app_logging(log_level: Optional[str] = None) -> None:
    """
    Initialize application logging.
    Should be called once at application startup.

    Args:
        log_level: Optional log level override
    """
    from app.core.config import settings

    level = log_level or getattr(settings, 'LOG_LEVEL', 'INFO')
    setup_logging(level)

    logger = get_logger(__name__)
    logger.info(f"Logging initialized at {level} level")
