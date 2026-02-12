"""Endpoint for allergens."""

from fastapi import APIRouter, HTTPException
from internal.database.dependency import database_dependency
from internal.queries.allergens import Querier as AllergensQuerier
from internal.queries.models import Allergen

router = APIRouter(prefix="/allergens", tags=["allergens"])


@router.get("/")
async def get_allergens(conn: database_dependency) -> list[Allergen]:
    """Get all allergens.

    Returns:
        all allergens

    Raises:
        HTTPException: if failed to get allergens
    """
    allergens = AllergensQuerier(conn).get_allergens()
    if not allergens:
        raise HTTPException(500, "failed to get allergens")
    return list(allergens)
