"""Endpoint for allergens."""

from fastapi import APIRouter, HTTPException, status
from internal.database.dependency import database_dependency
from internal.queries.allergens import Querier as AllergensQuerier
from internal.queries.models import Allergen

router = APIRouter(prefix="/allergens", tags=["allergens"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all allergens",
    description="Retrieves a list of all defined allergens.",
)
async def get_allergens(conn: database_dependency) -> list[Allergen]:
    """Get all allergens.

    Returns:
        all allergens

    Raises:
        HTTPException: if failed to get allergens
    """
    allergens = AllergensQuerier(conn).get_allergens()
    if allergens is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get allergens",
        )
    return list(allergens)
