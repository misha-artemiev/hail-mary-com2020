"""Endpoints for general reports."""

from fastapi import APIRouter, status
from internal.queries.models import AdminIssueType, SellerIssueType

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/admin",
    status_code=status.HTTP_200_OK,
    summary="Get admin issue types",
    description="Retrieves a list of all possible admin issue types.",
    tags=["reports"],
)
async def get_admin_issue_types() -> list[AdminIssueType]:
    """Get admin issue types.

    Returns:
        list of admin issue types
    """
    return list(AdminIssueType)


@router.get(
    "/seller",
    status_code=status.HTTP_200_OK,
    summary="Get seller issue types",
    description="Retrieves a list of all possible seller issue types.",
    tags=["reports"],
)
async def get_seller_issue_types() -> list[SellerIssueType]:
    """Get seller issue types.

    Returns:
        list of seller issue types
    """
    return list(SellerIssueType)
