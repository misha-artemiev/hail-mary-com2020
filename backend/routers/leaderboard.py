from fastapi import APIRouter, HTTPException, status
from enum import Enum
from internal.database.dependency import database_dependency
from internal.queries.user import AsyncQuerier as UserQuerier

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

class LeaderboardTypes(Enum):
    RESERVATIONS = "reservations"
    CARBON_DIOXIDE = "carbon_dioxide"

@router.get(path="/")
async def get_leaderboard_types() -> list[str]:
    return [leaderboard_type.value for leaderboard_type in LeaderboardTypes]

@router.get(path="/leaderboard/{leaderboard_type}")
async def get_leaderboard(leaderboard_type: LeaderboardTypes, limit: int, conn: database_dependency) -> list[tuple[str,int]]:
    user_querier = UserQuerier(conn)
    match leaderboard_type:
        case LeaderboardTypes.RESERVATIONS:
            if (leaderboard := user_querier.leaderboard_reservations(limit=limit)) == None:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get leaderboard")
            return [(user.username, user.reservation_count) async for user in leaderboard]
        case LeaderboardTypes.CARBON_DIOXIDE:
            if (leaderboard := user_querier.leaderboard_carbon_dioxide(limit=limit)) == None:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get leaderboard")
            return [(user.username, int(user.total_carbon_dioxide)) async for user in leaderboard]
