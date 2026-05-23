"""
Tenant database models.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Tenant(SQLModel, table=True):
    """
    Tenant model representing an organization in the multi-tenant system.
    Each tenant has isolated data and can have custom AI prompts.
    """
    __tablename__ = "tenants"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    custom_prompt: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (forward references to avoid circular imports)
    documents: List["Document"] = Relationship(back_populates="tenant", cascade_delete=True)
    embeddings: List["DocumentEmbedding"] = Relationship(back_populates="tenant", cascade_delete=True)
