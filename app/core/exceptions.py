"""
Custom exceptions and global exception handlers for the application.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException

# Custom Exception Classes
class TenantNotFoundError(Exception):
    """Raised when a tenant is not found in the database."""
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        super().__init__(f"Tenant with ID {tenant_id} not found")


class DocumentNotFoundError(Exception):
    """Raised when a document is not found in the database."""
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(f"Document with ID {document_id} not found")


class InvalidTenantHeaderError(Exception):
    """Raised when X-Tenant-ID header is missing or invalid."""
    def __init__(self, message: str = "Missing or invalid X-Tenant-ID header"):
        super().__init__(message)


class EmbeddingProcessingError(Exception):
    """Raised when embedding processing fails."""
    def __init__(self, message: str, document_id: Optional[int] = None):
        self.document_id = document_id
        super().__init__(message)


class StorageError(Exception):
    """Raised when file storage operations fail."""
    def __init__(self, message: str):
        super().__init__(message)


class LLMError(Exception):
    """Raised when LLM generation fails."""
    def __init__(self, message: str):
        super().__init__(message)

class HTTPException(FastAPIHTTPException):
    """
    Custom wrapper to allow 'from app.core.exceptions import HTTPException'
    while preserving full FastAPI/Starlette compatibility.
    """
    def __init__(self, status_code: int, detail: Optional[str] = None, headers: Optional[dict] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class STTError(Exception):
    """Raised when speech-to-text transcription fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

# Global Exception Handlers
async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError) -> JSONResponse:
    """Handle TenantNotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "code": "TENANT_NOT_FOUND",
            "message": str(exc),
            "data": None
        }
    )


async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:
    """Handle DocumentNotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "code": "DOCUMENT_NOT_FOUND",
            "message": str(exc),
            "data": None
        }
    )


async def invalid_tenant_header_handler(request: Request, exc: InvalidTenantHeaderError) -> JSONResponse:
    """Handle InvalidTenantHeaderError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "code": "INVALID_TENANT_HEADER",
            "message": str(exc),
            "data": None
        }
    )


async def embedding_processing_error_handler(request: Request, exc: EmbeddingProcessingError) -> JSONResponse:
    """Handle EmbeddingProcessingError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": "EMBEDDING_PROCESSING_FAILED",
            "message": str(exc),
            "data": None
        }
    )


async def storage_error_handler(request: Request, exc: StorageError) -> JSONResponse:
    """Handle StorageError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": "STORAGE_ERROR",
            "message": str(exc),
            "data": None
        }
    )


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    """Handle LLMError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": "LLM_ERROR",
            "message": str(exc),
            "data": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic/FastAPI request validation errors and format them into our standard envelope."""
    
    # Extract the custom messages from the validation errors
    error_messages = []
    for error in exc.errors():
        # e.g., "body -> name: Only lowercase letters..."
        location = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{location}: {msg}")
    
    # Combine messages into a clean, single string
    full_message = "Validation failed: " + "; ".join(error_messages)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": "VALIDATION_ERROR",
            "message": full_message,
            "data": None
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Temporary debug version of your catch-all handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "code": "INTERNAL_SERVER_ERROR",
            "message": f"Debug Info: {str(exc)}", # <-- This shows the hidden error message
            "data": None
        }
    )

async def http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
    """Interceptors native or custom HTTPExceptions to return our standard envelope."""
    
    # Simple dynamic status code string mapper
    code_mapping = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR"
    }
    error_code = code_mapping.get(exc.status_code, "HTTP_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": error_code,
            "message": exc.detail,
            "data": None
        }
    )

def register_exception_handlers(app):
    """
    Register all custom exception handlers with the FastAPI app.
    Call this function in main.py after creating the app instance.
    """
    app.add_exception_handler(TenantNotFoundError, tenant_not_found_handler)
    app.add_exception_handler(DocumentNotFoundError, document_not_found_handler)
    app.add_exception_handler(InvalidTenantHeaderError, invalid_tenant_header_handler)
    app.add_exception_handler(EmbeddingProcessingError, embedding_processing_error_handler)
    app.add_exception_handler(StorageError, storage_error_handler)
    app.add_exception_handler(LLMError, llm_error_handler)
    app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
