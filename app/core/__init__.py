"""
Core infrastructure module.
Contains shared utilities, configuration, and base classes.
"""
from app.core.config import settings
from app.core.constants import DocumentStatus, ResponseCode, ErrorMessage
from app.core.exceptions import (
    TenantNotFoundError,
    DocumentNotFoundError,
    InvalidTenantHeaderError,
    EmbeddingProcessingError,
    StorageError,
    LLMError,
    register_exception_handlers
)
from app.core.responses import Envelope, success_response, error_response
from app.core.logging import get_logger, init_app_logging
from app.core.chunking import chunk_text_smart, chunk_text_with_metadata
from app.core.database import engine, init_db, get_session

__all__ = [
    # Config
    "settings",
    # Constants
    "DocumentStatus",
    "ResponseCode",
    "ErrorMessage",
    # Exceptions
    "TenantNotFoundError",
    "DocumentNotFoundError",
    "InvalidTenantHeaderError",
    "EmbeddingProcessingError",
    "StorageError",
    "LLMError",
    "register_exception_handlers",
    # Responses
    "Envelope",
    "success_response",
    "error_response",
    # Logging
    "get_logger",
    "init_app_logging",
    # Chunking
    "chunk_text_smart",
    "chunk_text_with_metadata",
    # Database
    "engine",
    "init_db",
    "get_session",
]
