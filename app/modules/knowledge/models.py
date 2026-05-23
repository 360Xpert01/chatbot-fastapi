"""
Document and embedding database models.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column


class Document(SQLModel, table=True):
    """
    Document model representing uploaded files in the knowledge base.
    Each document belongs to a tenant and can have multiple embeddings.
    """
    __tablename__ = "documents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", ondelete="CASCADE")
    filename: str = Field(max_length=255)
    file_url: str
    file_type: Optional[str] = Field(default=None, max_length=50)
    file_size: Optional[int] = Field(default=None)
    embedding_status: str = Field(default="pending", max_length=20)  # pending | processing | done | failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (forward references to avoid circular imports)
    tenant: "Tenant" = Relationship(back_populates="documents")
    embeddings: List["DocumentEmbedding"] = Relationship(back_populates="document", cascade_delete=True)


class DocumentEmbedding(SQLModel, table=True):
    """
    Document embedding model representing vector embeddings of text chunks.
    Each embedding is a chunk of a document with its vector representation.
    """
    __tablename__ = "document_embeddings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", ondelete="CASCADE")
    document_id: uuid.UUID = Field(foreign_key="documents.id", ondelete="CASCADE")
    chunk_content: str
    # 768 dimensions matches text-embedding-004 from Google Gemini
    embedding: List[float] = Field(sa_column=Column(Vector(768), nullable=False))

    # Relationships
    tenant: "Tenant" = Relationship(back_populates="embeddings")
    document: Document = Relationship(back_populates="embeddings")
