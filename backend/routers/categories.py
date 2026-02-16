"""Endpoint for categories."""

from fastapi import APIRouter, HTTPException
from internal.database.dependency import database_dependency
from internal.queries.category import Querier as CategoriesQuerier
from internal.queries.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
async def get_categories(conn: database_dependency) -> list[Category]:
    """Get all categories.

    Returns:
        all categories

    Raises:
        HTTPException: if failed to get categories
    """
    categories = CategoriesQuerier(conn).get_categories()
    if not categories:
        raise HTTPException(500, "failed to get allergens")
    return list(categories)
