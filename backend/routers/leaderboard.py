"""Endpoints for leaderboard."""

from enum import Enum

from fastapi import APIRouter, HTTPException, status
from internal.database.dependency import database_dependency
from internal.queries.user import AsyncQuerier as UserQuerier

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardTypes(Enum):
    """Leaderboard types."""

    RESERVATIONS = "reservations"
    CARBON_DIOXIDE = "carbon_dioxide"


@router.get(
    path="/",
    summary="Get leaderboard types",
    description="Retrieves all available leaderboard types.",
)
async def get_leaderboard_types() -> list[str]:
    """Get all leaderboard types.

    Returns:
        leaderboard types
    """
    return [leaderboard_type.value for leaderboard_type in LeaderboardTypes]


@router.get(
    path="/leaderboard/{leaderboard_type}",
    summary="Get leaderboard",
    description=(
        "Retrieves the leaderboard for a specific type, "
        "returning top users by reservation count or carbon dioxide saved."
    ),
)
async def get_leaderboard(
    leaderboard_type: LeaderboardTypes, limit: int, conn: database_dependency
) -> list[tuple[str, int]]:
    """Get leaderboard of a type.

    Args:
        leaderboard_type: leaderboard type
        limit: how many users to show
        conn: database connection

    Returns:
        leaderboard of users for a type

    Raises:
        HTTPException: if failed to get leaderboard
    """
    user_querier = UserQuerier(conn)
    match leaderboard_type:
        case LeaderboardTypes.RESERVATIONS:
            if (
                leaderboard_reservations := user_querier.leaderboard_reservations(
                    limit=limit
                )
            ) is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get leaderboard"
                )
            return [
                (user.username, user.reservation_count)
                async for user in leaderboard_reservations
            ]
        case LeaderboardTypes.CARBON_DIOXIDE:
            if (
                leaderboard_carbon_dioxide := user_querier.leaderboard_carbon_dioxide(
                    limit=limit
                )
            ) is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get leaderboard"
                )
            return [
                (user.username, int(user.total_carbon_dioxide))
                async for user in leaderboard_carbon_dioxide
            ]
