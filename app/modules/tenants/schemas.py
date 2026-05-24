"""
Tenant request/response schemas.
"""
import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

NAME_REGEX = r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$"

class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    name: str
    email: EmailStr
    custom_prompt: Optional[str] = None
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not re.fullmatch(NAME_REGEX, value):
            raise ValueError(
                "Only lowercase letters, numbers, '-' and '_' are allowed. No spaces."
            )
        return value

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
    created_at: datetime  
    updated_at: datetime  

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    total_count: int
    skip: int
    limit: int

class PaginatedTenantResponse(BaseModel):
    items: List[TenantResponse]
    pagination: PaginationMeta