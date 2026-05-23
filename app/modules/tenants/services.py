"""
Tenant business logic and service layer.
"""
import uuid
from typing import List
from sqlmodel import Session, select
from app.modules.tenants.models import Tenant
from app.modules.tenants.schemas import TenantCreate, TenantUpdate
from app.core.logging import get_logger
from app.core.exceptions import TenantNotFoundError

logger = get_logger(__name__)


class TenantService:
    """Service class for tenant management operations."""

    @staticmethod
    def create_tenant(tenant_data: TenantCreate, db: Session) -> Tenant:
        """
        Create a new tenant.

        Args:
            tenant_data: Tenant creation data
            db: Database session

        Returns:
            Created tenant instance
        """
        logger.info(f"Creating tenant: {tenant_data.name}")

        new_tenant = Tenant(
            name=tenant_data.name,
            email=tenant_data.email,
            custom_prompt=tenant_data.custom_prompt
        )

        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)

        logger.info(f"Tenant created successfully: {new_tenant.id}")
        return new_tenant

    @staticmethod
    def get_tenant(tenant_id: uuid.UUID, db: Session) -> Tenant:
        """
        Get a tenant by ID.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Returns:
            Tenant instance

        Raises:
            TenantNotFoundError: If tenant not found
        """
        logger.debug(f"Fetching tenant: {tenant_id}")

        tenant = db.get(Tenant, tenant_id)
        if not tenant:
            logger.warning(f"Tenant not found: {tenant_id}")
            raise TenantNotFoundError(str(tenant_id))

        return tenant

    @staticmethod
    def get_tenant_by_email(email: str, db: Session) -> Tenant:
        """
        Get a tenant by email.

        Args:
            email: Tenant email
            db: Database session

        Returns:
            Tenant instance

        Raises:
            TenantNotFoundError: If tenant not found
        """
        logger.debug(f"Fetching tenant by email: {email}")

        tenant = db.exec(select(Tenant).where(Tenant.email == email)).first()
        if not tenant:
            logger.warning(f"Tenant not found with email: {email}")
            raise TenantNotFoundError(f"email: {email}")

        return tenant

    @staticmethod
    def list_tenants(db: Session) -> List[Tenant]:
        """
        List all tenants.

        Args:
            db: Database session

        Returns:
            List of all tenants
        """
        logger.debug("Listing all tenants")

        tenants = db.exec(select(Tenant)).all()

        logger.info(f"Retrieved {len(tenants)} tenants")
        return tenants

    @staticmethod
    def update_tenant(
        tenant_id: uuid.UUID,
        tenant_data: TenantUpdate,
        db: Session
    ) -> Tenant:
        """
        Update a tenant.

        Args:
            tenant_id: Tenant UUID
            tenant_data: Updated tenant data
            db: Database session

        Returns:
            Updated tenant instance

        Raises:
            TenantNotFoundError: If tenant not found
        """
        logger.info(f"Updating tenant: {tenant_id}")

        tenant = db.get(Tenant, tenant_id)
        if not tenant:
            logger.warning(f"Tenant not found for update: {tenant_id}")
            raise TenantNotFoundError(str(tenant_id))

        tenant.name = tenant_data.name
        if tenant_data.email is not None:
            tenant.email = tenant_data.email
        tenant.custom_prompt = tenant_data.custom_prompt

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        logger.info(f"Tenant updated successfully: {tenant_id}")
        return tenant

    @staticmethod
    def delete_tenant(tenant_id: uuid.UUID, db: Session) -> None:
        """
        Delete a tenant and clean up associated resources.

        Args:
            tenant_id: Tenant UUID
            db: Database session

        Raises:
            TenantNotFoundError: If tenant not found

        Note:
            This will cascade delete all associated documents and embeddings.
            Storage cleanup is handled separately in the router.
        """
        logger.info(f"Deleting tenant: {tenant_id}")

        tenant = db.get(Tenant, tenant_id)
        if not tenant:
            logger.warning(f"Tenant not found for deletion: {tenant_id}")
            raise TenantNotFoundError(str(tenant_id))

        db.delete(tenant)
        db.commit()

        logger.info(f"Tenant deleted successfully: {tenant_id}")
