"""Endpoints for leaderboard."""

from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, status
from internal.database.dependency import database_dependency
from internal.queries.user import AsyncQuerier as UserQuerier

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardTypes(Enum):
    """Leaderboard types."""

    RESERVATIONS = "reservations"
    CARBON_DIOXIDE = "carbon_dioxide"
    MONEY_SAVED = "money_saved"
    TOTAL_SPENT = "total_spent"
    WEEKLY_STREAK = "weekly_streak"


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


def _check_leaderboard_data(data: AsyncIterator[Any] | None) -> AsyncIterator[Any]:
    """Check that leaderboard data is not None.

    Args:
        data: The async iterator from the querier

    Returns:
        The async iterator if not None

    Raises:
        HTTPException: if data is None
    """
    if data is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get leaderboard"
        )
    return data


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
    """
    user_querier = UserQuerier(conn)
    match leaderboard_type:
        case LeaderboardTypes.RESERVATIONS:
            data = _check_leaderboard_data(
                user_querier.leaderboard_reservations(limit=limit)
            )
            return [(user.username, user.reservation_count) async for user in data]
        case LeaderboardTypes.CARBON_DIOXIDE:
            data = _check_leaderboard_data(
                user_querier.leaderboard_carbon_dioxide(limit=limit)
            )
            return [
                (user.username, int(user.total_carbon_dioxide)) async for user in data
            ]
        case LeaderboardTypes.MONEY_SAVED:
            data = _check_leaderboard_data(
                user_querier.leaderboard_money_saved(limit=limit)
            )
            return [(user.username, int(user.total_money_saved)) async for user in data]
        case LeaderboardTypes.TOTAL_SPENT:
            data = _check_leaderboard_data(
                user_querier.leaderboard_total_spent(limit=limit)
            )
            return [(user.username, int(user.total_spent)) async for user in data]
        case LeaderboardTypes.WEEKLY_STREAK:
            data = _check_leaderboard_data(
                user_querier.leaderboard_weekly_streak(limit=limit)
            )
            return [(user.username, user.streak_weeks) async for user in data]
