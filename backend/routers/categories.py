"""Endpoint for categories."""

from fastapi import APIRouter, HTTPException, status
from internal.database.dependency import database_dependency
from internal.queries.category import AsyncQuerier as CategoriesQuerier
from internal.queries.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all categories",
    description="Retrieves a list of all defined bundle categories.",
)
async def get_categories(conn: database_dependency) -> list[Category]:
    """Get all categories.

    Returns:
        all categories

    Raises:
        HTTPException: if failed to get categories
    """
    categories = [item async for item in CategoriesQuerier(conn).get_categories()]
    if categories is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get categories",
        )
    return list(categories)
