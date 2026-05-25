"""
Tenant management API endpoints.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.responses import Envelope, success_response
from app.core.constants import ResponseCode
from app.modules.tenants.schemas import TenantCreate, TenantUpdate, TenantResponse, PaginatedTenantResponse, PaginationMeta
from app.modules.tenants.services import TenantService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.post("", response_model=Envelope[TenantResponse], status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_session)
) -> Envelope[TenantResponse]:
    """
    Create a new tenant.

    Args:
        tenant: Tenant creation data
        db: Database session

    Returns:
        Envelope containing the created tenant
    """
    logger.info(f"POST /api/v1/tenants - Creating tenant: {tenant.name}")

    new_tenant = TenantService.create_tenant(tenant, db)

    return success_response(
        code=ResponseCode.TENANT_CREATED,
        message="Tenant created successfully",
        data=TenantResponse.model_validate(new_tenant)
    )


@router.get("", response_model=Envelope[PaginatedTenantResponse]) # <-- Updated response model
def list_tenants(
    name: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
) -> Envelope[PaginatedTenantResponse]:
    """
    List all tenants with professional metadata pagination.
    """
    logger.info(
        f"GET /api/v1/tenants - Filters: name={name}, email={email}, "
        f"Pagination: skip={skip}, limit={limit}"
    )

    # Fetch result dictionary containing data list and integer count
    result = TenantService.list_tenants(
        db=db, 
        name=name, 
        email=email, 
        skip=skip, 
        limit=limit
    )

    # Format into our paginated schema payload
    paginated_data = PaginatedTenantResponse(
        items=[TenantResponse.model_validate(t) for t in result["items"]],
        pagination=PaginationMeta(
            total_count=result["total_count"],
            skip=skip,
            limit=limit
        )
    )

    return success_response(
        code=ResponseCode.TENANTS_LISTED,
        message="Tenants retrieved successfully",
        data=paginated_data
    )

@router.get("/search", response_model=Envelope[TenantResponse])
def search_tenant_by_email(
    email: str,
    db: Session = Depends(get_session)
) -> Envelope[TenantResponse]:
    """
    Search for a tenant by email.

    Args:
        email: Tenant email
        db: Database session

    Returns:
        Envelope containing the tenant data

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
    """
    logger.info(f"GET /api/v1/tenants/search?email={email}")

    tenant = TenantService.get_tenant_by_email(email, db)

    return success_response(
        code=ResponseCode.TENANT_RETRIEVED,
        message="Tenant retrieved successfully",
        data=TenantResponse.model_validate(tenant)
    )


@router.get("/{tenant_id}", response_model=Envelope[TenantResponse])
def get_tenant(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_session)
) -> Envelope[TenantResponse]:
    """
    Get a specific tenant by ID.

    Args:
        tenant_id: Tenant UUID
        db: Database session

    Returns:
        Envelope containing the tenant data

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
    """
    logger.info(f"GET /api/v1/tenants/{tenant_id}")

    tenant = TenantService.get_tenant(tenant_id, db)

    return success_response(
        code=ResponseCode.TENANT_RETRIEVED,
        message="Tenant retrieved successfully",
        data=TenantResponse.model_validate(tenant)
    )


@router.put("/{tenant_id}", response_model=Envelope[TenantResponse])
def update_tenant(
    tenant_id: uuid.UUID,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_session)
) -> Envelope[TenantResponse]:
    """
    Update a tenant.

    Args:
        tenant_id: Tenant UUID
        tenant_data: Updated tenant data
        db: Database session

    Returns:
        Envelope containing the updated tenant

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
    """
    logger.info(f"PUT /api/v1/tenants/{tenant_id}")

    updated_tenant = TenantService.update_tenant(tenant_id, tenant_data, db)

    return success_response(
        code=ResponseCode.TENANT_UPDATED,
        message="Tenant updated successfully",
        data=TenantResponse.model_validate(updated_tenant)
    )


@router.delete("/{tenant_id}", response_model=Envelope[None])
def delete_tenant(
    tenant_id: uuid.UUID,
    db: Session = Depends(get_session)
) -> Envelope[None]:
    """
    Delete a tenant and all associated resources.

    This will:
    1. Delete all files from cloud storage
    2. Cascade delete all documents and embeddings from database
    3. Delete the tenant record

    Args:
        tenant_id: Tenant UUID
        db: Database session

    Returns:
        Envelope with success confirmation

    Raises:
        TenantNotFoundError: If tenant not found (handled by global exception handler)
    """
    logger.info(f"DELETE /api/v1/tenants/{tenant_id}")

    # Import here to avoid circular dependency
    from app.modules.knowledge.models import Document
    from app.services.storage import StorageService

    # Get tenant to ensure it exists (will raise TenantNotFoundError if not)
    TenantService.get_tenant(tenant_id, db)

    # Clean up storage files before deleting tenant
    docs = db.exec(select(Document).where(Document.tenant_id == tenant_id)).all()
    for doc in docs:
        StorageService.delete_file(doc.file_url)

    # Delete tenant (cascade deletes documents and embeddings)
    TenantService.delete_tenant(tenant_id, db)

    return success_response(
        code=ResponseCode.TENANT_DELETED,
        message="Tenant deleted successfully",
        data=None
    )
