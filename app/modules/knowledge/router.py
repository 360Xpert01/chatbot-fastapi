"""
Document management API endpoints.
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.responses import Envelope, success_response
from app.core.constants import ResponseCode
from app.modules.knowledge.schemas import DocumentResponse
from app.modules.knowledge.services import DocumentService
from app.modules.tenants.services import TenantService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["knowledge"])


@router.get("/{tenant_id}/files", response_model=Envelope[List[DocumentResponse]])
def list_tenant_files(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_session)
) -> Envelope[List[DocumentResponse]]:
    """
    List all documents for a tenant.

    Args:
        tenant_id: Tenant UUID
        db: Database session

    Returns:
        Envelope containing list of documents

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
    """
    logger.info(f"GET /api/v1/tenants/{tenant_id}/files")

    # Verify tenant exists
    TenantService.get_tenant(tenant_id, db)

    # Get documents
    documents = DocumentService.list_documents(tenant_id, db)

    return success_response(
        code=ResponseCode.FILES_LISTED,
        message="Files retrieved successfully",
        data=[DocumentResponse.model_validate(doc) for doc in documents]
    )


@router.post("/{tenant_id}/files/upload", response_model=Envelope[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_tenant_file(
    tenant_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_session)
) -> Envelope[DocumentResponse]:
    """
    Upload a document and process its embeddings.

    This endpoint:
    1. Uploads the file to cloud storage
    2. Creates a document record
    3. Extracts text and chunks it using sentence-aware splitting
    4. Generates embeddings for each chunk
    5. Stores embeddings in the database

    Args:
        tenant_id: Tenant UUID
        file: File to upload
        db: Database session

    Returns:
        Envelope containing the created document

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
        StorageError: If file upload fails (handled by global exception handler)
    """
    logger.info(f"POST /api/v1/tenants/{tenant_id}/files/upload - Uploading: {file.filename}")

    # Verify tenant exists
    TenantService.get_tenant(tenant_id, db)

    # Upload and process document
    document = await DocumentService.upload_document(tenant_id, file, db)

    return success_response(
        code=ResponseCode.FILE_UPLOADED,
        message="File uploaded and indexed successfully",
        data=DocumentResponse.model_validate(document)
    )


@router.post("/{tenant_id}/files/{file_id}/retry", response_model=Envelope[DocumentResponse])
async def retry_file_embedding(
    tenant_id: uuid.UUID,
    file_id: uuid.UUID,
    db: Session = Depends(get_session)
) -> Envelope[DocumentResponse]:
    """
    Retry embedding generation for a failed document.

    This endpoint:
    1. Verifies the document exists and belongs to the tenant
    2. Clears old embeddings
    3. Re-downloads the file from storage
    4. Re-processes embeddings with sentence-aware chunking

    Args:
        tenant_id: Tenant UUID
        file_id: Document UUID
        db: Database session

    Returns:
        Envelope containing the updated document

    Raises:
        DocumentNotFoundError: If document not found (handled by global exception handler)
        EmbeddingProcessingError: If retry fails (handled by global exception handler)
    """
    logger.info(f"POST /api/v1/tenants/{tenant_id}/files/{file_id}/retry")

    # Retry embeddings
    document = await DocumentService.retry_embeddings(tenant_id, file_id, db)

    return success_response(
        code=ResponseCode.EMBEDDINGS_RETRY_STARTED,
        message="File reindexed successfully",
        data=DocumentResponse.model_validate(document)
    )


@router.delete("/{tenant_id}/files/{file_id}", response_model=Envelope[None])
def delete_tenant_file(
    tenant_id: uuid.UUID,
    file_id: uuid.UUID,
    db: Session = Depends(get_session)
) -> Envelope[None]:
    """
    Delete a document and its embeddings.

    This will:
    1. Delete the file from cloud storage
    2. Delete the document record (cascade deletes embeddings)

    Args:
        tenant_id: Tenant UUID
        file_id: Document UUID
        db: Database session

    Returns:
        Envelope with success confirmation

    Raises:
        DocumentNotFoundError: If document not found (handled by global exception handler)
    """
    logger.info(f"DELETE /api/v1/tenants/{tenant_id}/files/{file_id}")

    # Delete document
    DocumentService.delete_document(tenant_id, file_id, db)

    return success_response(
        code=ResponseCode.FILE_DELETED,
        message="File deleted successfully",
        data=None
    )
