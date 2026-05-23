"""
Tenant request/response schemas.
"""
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    name: str
    email: EmailStr
    custom_prompt: Optional[str] = None


class TenantUpdate(BaseModel):
    """Schema for updating an existing tenant."""
    name: str
    email: Optional[EmailStr] = None
    custom_prompt: Optional[str] = None


class TenantResponse(BaseModel):
    """Schema for tenant response data."""
    id: uuid.UUID
    name: str
    email: str
    custom_prompt: Optional[str]

    class Config:
        from_attributes = True
