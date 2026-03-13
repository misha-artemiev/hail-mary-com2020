"""Endpoints for admins."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Security, status
from internal.auth.creation import CreateAdminForm, create_admin
from internal.auth.middleware import root_auth
from internal.database.dependency import database_dependency
from internal.queries.models import Admin
from internal.queries.admin import AsyncQuerier as AdminQuerier, SetIsAdminActiveParams

router = APIRouter(prefix="/admins", tags=["admins"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create admin",
    description="Create admin by root user",
    tags=["root admin"],
)
async def register_admin(
    form: CreateAdminForm,
    conn: database_dependency,
    _: Annotated[None, Security(root_auth)],
) -> None:
    """Create admin by root user.

    Args:
        form: new admin information
        conn: database connection
    """
    await create_admin(form, conn)

@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate admin",
    description="Deactivate admin by root user"
)
async def deactivate_admin(admin_id: int, conn: database_dependency, _: Annotated[None, Security(root_auth)]) -> Admin:
    """Deactivate admin.

    Args:
        admin_id: admin id
        conn: database connection

    Returns:
        deactivated admin

    Raises:
        HTTPException: if failed to find admin
    """
    admin = await AdminQuerier(conn).set_is_admin_active(SetIsAdminActiveParams(user_id=admin_id,active=False))
    if not admin:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No admin was found")
    return admin
