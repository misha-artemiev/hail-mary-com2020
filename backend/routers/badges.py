from fastapi import APIRouter
from internal.database.dependency import database_dependency
from internal.queries.models import Badge
from internal.queries.badge import AsyncQuerier as BadgeQuerier

router = APIRouter(prefix="/badges", tags=["badges"])

@router.get("/", status_code=200,
    summary="Get badges",
    description="Get all badges",
)
async def get_badges(conn: database_dependency) -> list[Badge]:
    return [badge async for badge in BadgeQuerier(conn).get_badges()]
