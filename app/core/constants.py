"""
Core constants for the multi-tenant chat application.
Centralizes all magic strings, status values, and response codes.
"""


class DocumentStatus:
    """Document processing status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ResponseCode:
    """API response codes for success scenarios."""
    # Tenant operations
    TENANT_CREATED = "TENANT_CREATED"
    TENANT_RETRIEVED = "TENANT_RETRIEVED"
    TENANT_UPDATED = "TENANT_UPDATED"
    TENANT_DELETED = "TENANT_DELETED"
    TENANTS_LISTED = "TENANTS_LISTED"

    # Document operations
    FILE_UPLOADED = "FILE_UPLOADED"
    FILE_DELETED = "FILE_DELETED"
    FILES_LISTED = "FILES_LISTED"
    EMBEDDINGS_RETRY_STARTED = "EMBEDDINGS_RETRY_STARTED"

    # Chat operations
    CHAT_COMPLETED = "CHAT_COMPLETED"


class ErrorMessage:
    """Error messages for various failure scenarios."""
    # Tenant errors
    TENANT_NOT_FOUND = "Tenant not found"
    TENANT_CREATION_FAILED = "Failed to create tenant"
    TENANT_UPDATE_FAILED = "Failed to update tenant"
    TENANT_DELETE_FAILED = "Failed to delete tenant"

    # Document errors
    DOCUMENT_NOT_FOUND = "Document not found"
    FILE_UPLOAD_FAILED = "Failed to upload file"
    FILE_DELETE_FAILED = "Failed to delete file"
    EMBEDDING_PROCESSING_FAILED = "Failed to process embeddings"

    # Validation errors
    INVALID_TENANT_HEADER = "Missing or invalid X-Tenant-ID header"
    INVALID_FILE_TYPE = "Invalid file type"
    FILE_TOO_LARGE = "File size exceeds maximum allowed"

    # Chat errors
    CHAT_FAILED = "Failed to generate chat response"
    NO_CONTEXT_FOUND = "No relevant context found for query"

    # General errors
    INTERNAL_SERVER_ERROR = "Internal server error"
    DATABASE_ERROR = "Database operation failed"
