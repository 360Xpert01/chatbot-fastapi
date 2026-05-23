"""
Document and embedding business logic and service layer.
"""
import uuid
import urllib.request
from typing import List
from sqlmodel import Session, select
from fastapi import UploadFile

from app.modules.knowledge.models import Document, DocumentEmbedding
from app.core.logging import get_logger
from app.core.exceptions import DocumentNotFoundError, EmbeddingProcessingError
from app.core.constants import DocumentStatus
from app.core.chunking import chunk_text_smart
from app.core.config import settings
from app.services.storage import StorageService
from app.services.embedding import EmbeddingService

logger = get_logger(__name__)


class DocumentService:
    """Service class for document and embedding management operations."""

    @staticmethod
    async def upload_document(
        tenant_id: uuid.UUID,
        file: UploadFile,
        db: Session
    ) -> Document:
        """
        Upload a document and process its embeddings.

        Pipeline:
        1. Upload file to cloud storage
        2. Create document record in database
        3. Extract text and chunk using sentence-aware splitting
        4. Generate embeddings for each chunk
        5. Store embeddings in database

        Args:
            tenant_id: Tenant UUID
            file: Uploaded file
            db: Database session

        Returns:
            Created document instance

        Raises:
            StorageError: If file upload fails
            EmbeddingProcessingError: If embedding generation fails
        """
        logger.info(f"Uploading document: {file.filename} for tenant: {tenant_id}")

        # Read file bytes
        file_bytes = await file.read()
        file_size = len(file_bytes)

        # Step 1: Upload to cloud storage
        file_url = StorageService.upload_file(file_bytes, file.filename)

        # Step 2: Create document record
        db_doc = Document(
            tenant_id=tenant_id,
            filename=file.filename,
            file_url=file_url,
            file_type=file.content_type,
            file_size=file_size,
            embedding_status=DocumentStatus.PENDING
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        # Step 3: Process embeddings synchronously
        try:
            db_doc.embedding_status = DocumentStatus.PROCESSING
            db.add(db_doc)
            db.commit()

            # Extract text
            raw_text = file_bytes.decode("utf-8", errors="ignore")
            logger.info(f"Extracted {len(raw_text)} characters from {file.filename}")

            # Use sentence-aware chunking (IMPROVEMENT: replaces naive character-based chunking)
            chunks = chunk_text_smart(
                raw_text,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                min_chunk_size=settings.MIN_CHUNK_SIZE
            )

            logger.info(f"Created {len(chunks)} chunks for {file.filename}")

            # Generate embeddings for each chunk
            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                logger.debug(f"Generating embedding for chunk {idx + 1}/{len(chunks)}")
                vector_values = EmbeddingService.get_embedding(chunk)

                db_embedding = DocumentEmbedding(
                    tenant_id=tenant_id,
                    document_id=db_doc.id,
                    chunk_content=chunk,
                    embedding=vector_values
                )
                db.add(db_embedding)

            # Mark as done
            db_doc.embedding_status = DocumentStatus.DONE
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            logger.info(f"Document processed successfully: {file.filename}")

        except Exception as exc:
            logger.error(f"Embedding processing failed for {file.filename}: {str(exc)}", exc_info=True)
            db_doc.embedding_status = DocumentStatus.FAILED
            db.add(db_doc)
            db.commit()
            # Don't raise - document is created but embeddings failed

        return db_doc

    @staticmethod
    async def retry_embeddings(
        tenant_id: uuid.UUID,
        file_id: uuid.UUID,
        db: Session
    ) -> Document:
        """
        Retry embedding generation for a failed document.

        Steps:
        1. Verify document exists and belongs to tenant
        2. Clear old embeddings
        3. Re-download file from storage
        4. Re-process embeddings with sentence-aware chunking

        Args:
            tenant_id: Tenant UUID
            file_id: Document UUID
            db: Database session

        Returns:
            Updated document instance

        Raises:
            DocumentNotFoundError: If document not found
            EmbeddingProcessingError: If retry fails
        """
        logger.info(f"Retrying embeddings for document: {file_id}")

        # Verify document exists and belongs to tenant
        doc = db.exec(
            select(Document).where(
                Document.id == file_id,
                Document.tenant_id == tenant_id
            )
        ).first()

        if not doc:
            logger.warning(f"Document not found: {file_id} for tenant: {tenant_id}")
            raise DocumentNotFoundError(file_id)

        try:
            # Clear old embeddings
            old_embeddings = db.exec(
                select(DocumentEmbedding).where(DocumentEmbedding.document_id == file_id)
            ).all()

            for old_emb in old_embeddings:
                db.delete(old_emb)

            logger.info(f"Cleared {len(old_embeddings)} old embeddings")

            # Reset status to processing
            doc.embedding_status = DocumentStatus.PROCESSING
            db.add(doc)
            db.commit()

            # Re-download file from storage
            logger.info(f"Re-downloading file from: {doc.file_url}")
            with urllib.request.urlopen(doc.file_url) as response:
                file_bytes = response.read()

            # Extract and chunk text with sentence-aware splitting
            raw_text = file_bytes.decode("utf-8", errors="ignore")
            chunks = chunk_text_smart(
                raw_text,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                min_chunk_size=settings.MIN_CHUNK_SIZE
            )

            logger.info(f"Re-created {len(chunks)} chunks for retry")

            # Re-generate embeddings
            for idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue

                logger.debug(f"Generating embedding for chunk {idx + 1}/{len(chunks)}")
                vector_values = EmbeddingService.get_embedding(chunk)

                db_embedding = DocumentEmbedding(
                    tenant_id=tenant_id,
                    document_id=doc.id,
                    chunk_content=chunk,
                    embedding=vector_values
                )
                db.add(db_embedding)

            # Mark as done
            doc.embedding_status = DocumentStatus.DONE
            db.add(doc)
            db.commit()
            db.refresh(doc)

            logger.info(f"Document retry successful: {file_id}")
            return doc

        except Exception as exc:
            logger.error(f"Retry failed for document {file_id}: {str(exc)}", exc_info=True)
            doc.embedding_status = DocumentStatus.FAILED
            db.add(doc)
            db.commit()
            raise EmbeddingProcessingError(f"Retry failed: {str(exc)}", file_id)

    @staticmethod
    def delete_document(
        tenant_id: uuid.UUID,
        file_id: uuid.UUID,
        db: Session
    ) -> None:
        """
        Delete a document and its embeddings.

        Args:
            tenant_id: Tenant UUID
            file_id: Document UUID
            db: Database session

        Raises:
            DocumentNotFoundError: If document not found
        """
        logger.info(f"Deleting document: {file_id}")

        doc = db.exec(
            select(Document).where(
                Document.id == file_id,
                Document.tenant_id == tenant_id
            )
        ).first()

        if not doc:
            logger.warning(f"Document not found: {file_id} for tenant: {tenant_id}")
            raise DocumentNotFoundError(file_id)

        # Delete from storage
        StorageService.delete_file(doc.file_url)

        # Delete from database (cascade deletes embeddings)
        db.delete(doc)
        db.commit()

        logger.info(f"Document deleted successfully: {file_id}")

    @staticmethod
    def list_documents(tenant_id: uuid.UUID, db: Session) -> List[Document]:
        """
        List all documents for a tenant.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            List of documents
        """
        logger.debug(f"Listing documents for tenant: {tenant_id}")

        documents = db.exec(
            select(Document).where(Document.tenant_id == tenant_id)
        ).all()

        logger.info(f"Retrieved {len(documents)} documents for tenant: {tenant_id}")
        return documents
