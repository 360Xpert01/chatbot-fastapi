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
from fastapi.responses import StreamingResponse
from functools import partial
import asyncio
from app.core.constants import DocumentStatus
from app.rag.chunking import chunk_text_smart
from app.rag.embedding import EmbeddingService
from app.rag.parsers import DocumentParser
from app.modules.knowledge.models import Document, DocumentEmbedding
from app.core.config import settings

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


@router.post("/{tenant_id}/files/upload", status_code=status.HTTP_201_CREATED)
async def upload_tenant_file(
    tenant_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_session)
):
    logger.info(f"POST /api/v1/tenants/{tenant_id}/files/upload - Uploading: {file.filename}")

    TenantService.get_tenant(tenant_id, db)

    file_bytes = await file.read()
    file_size = len(file_bytes)
    filename = file.filename
    content_type = file.content_type

    async def event_stream():
        import json
        import os
        from app.services.storage import StorageService

        try:
            yield json.dumps({"stage": "uploading", "pct": 5}) + "\n"

            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext not in settings.ALLOWED_FILE_EXTENSIONS:
                from app.core.constants import ErrorMessage
                yield json.dumps({"stage": "error", "message": ErrorMessage.INVALID_FILE_TYPE}) + "\n"
                return

            yield json.dumps({"stage": "uploading", "pct": 15}) + "\n"
            loop = asyncio.get_event_loop()
            file_url = await loop.run_in_executor(
                None, partial(StorageService.upload_file, file_bytes, filename)
            )

            db_doc = Document(
                tenant_id=tenant_id,
                filename=filename,
                file_url=file_url,
                file_type=content_type,
                file_size=file_size,
                embedding_status=DocumentStatus.PROCESSING
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            yield json.dumps({"stage": "parsing", "pct": 25}) + "\n"

            raw_text = await loop.run_in_executor(
                None, partial(DocumentParser.extract_text, file_bytes, filename)
            )

            yield json.dumps({"stage": "chunking", "pct": 35}) + "\n"

            chunks = chunk_text_smart(
                raw_text,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                min_chunk_size=settings.MIN_CHUNK_SIZE
            )

            if not chunks:
                db_doc.embedding_status = DocumentStatus.FAILED
                db.add(db_doc)
                db.commit()
                yield json.dumps({"stage": "error", "message": "No content extracted from file"}) + "\n"
                return

            total = len(chunks)
            yield json.dumps({"stage": "embedding", "pct": 40, "chunk": 0, "total": total}) + "\n"

            BATCH = 10
            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                vector_values = await loop.run_in_executor(
                    None, partial(EmbeddingService.get_embedding, chunk)
                )
                db.add(DocumentEmbedding(
                    tenant_id=tenant_id,
                    document_id=db_doc.id,
                    chunk_content=chunk,
                    embedding=vector_values
                ))

                if (idx + 1) % BATCH == 0:
                    db.commit()

                pct = 40 + int((idx + 1) / total * 55)
                yield json.dumps({"stage": "embedding", "pct": pct, "chunk": idx + 1, "total": total}) + "\n"

            db.commit()
            db_doc.embedding_status = DocumentStatus.DONE
            db.add(db_doc)
            db.commit()

            yield json.dumps({
                "stage": "done",
                "pct": 100,
                "document_id": str(db_doc.id)
            }) + "\n"

        except Exception as exc:
            logger.error(f"Upload failed for {filename}: {exc}", exc_info=True)
            yield json.dumps({"stage": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

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
