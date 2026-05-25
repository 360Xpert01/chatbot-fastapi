"""
Standardized API response envelope pattern.
All API endpoints should return responses using this structure.
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel


T = TypeVar('T')


class Envelope(BaseModel, Generic[T]):
    """
    Generic envelope for all API responses.

    Attributes:
        success: Whether the operation was successful
        code: Response code (e.g., TENANT_CREATED, FILE_UPLOADED)
        message: Human-readable message
        data: Optional response data of type T
    """
    success: bool
    code: str
    message: str
    data: Optional[T] = None

    class Config:
        # Allow arbitrary types for generic support
        arbitrary_types_allowed = True


def success_response(code: str, message: str, data: T = None) -> Envelope[T]:
    """
    Create a standardized success response.

    Args:
        code: Response code constant (e.g., ResponseCode.TENANT_CREATED)
        message: Human-readable success message
        data: Optional response data

    Returns:
        Envelope with success=True

    Example:
        >>> success_response(
        ...     ResponseCode.TENANT_CREATED,
        ...     "Tenant created successfully",
        ...     tenant_data
        ... )
    """
    return Envelope(
        success=True,
        code=code,
        message=message,
        data=data
    )


def error_response(code: str, message: str) -> Envelope[None]:
    """
    Create a standardized error response.

    Args:
        code: Error code constant (e.g., "TENANT_NOT_FOUND")
        message: Human-readable error message

    Returns:
        Envelope with success=False and data=None

    Example:
        >>> error_response(
        ...     "TENANT_NOT_FOUND",
        ...     ErrorMessage.TENANT_NOT_FOUND
        ... )
    """
    return Envelope(
        success=False,
        code=code,
        message=message,
        data=None
    )
