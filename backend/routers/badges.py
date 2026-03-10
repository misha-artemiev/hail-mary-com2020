"""Endpoints for badges."""

from fastapi import APIRouter
from internal.database.dependency import database_dependency
from internal.queries.badge import AsyncQuerier as BadgeQuerier
from internal.queries.models import Badge

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("/", status_code=200, summary="Get badges", description="Get all badges")
async def get_badges(conn: database_dependency) -> list[Badge]:
    """Get all badges.

    Args:
      conn: database connection

    Returns:
      list of badges
    """
    return [badge async for badge in BadgeQuerier(conn).get_badges()]
