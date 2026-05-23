"""
Tenant request/response schemas.
"""
import uuid
from typing import Optional
from pydantic import BaseModel


class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    name: str
    custom_prompt: Optional[str] = None


class TenantUpdate(BaseModel):
    """Schema for updating an existing tenant."""
    name: str
    custom_prompt: Optional[str] = None


class TenantResponse(BaseModel):
    """Schema for tenant response data."""
    id: uuid.UUID
    name: str
    custom_prompt: Optional[str]

    class Config:
        from_attributes = True
