"""
Document request/response schemas.
"""
import uuid
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Schema for document response data."""
    id: uuid.UUID
    filename: str
    file_url: str
    embedding_status: str

    class Config:
        from_attributes = True
