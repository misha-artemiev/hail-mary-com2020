from fastapi import APIRouter
from enum import Enum

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

class LeaderboardTypes(Enum):
    RESERVATIONS = 0
    CARBON_DIOXIDE = 1

@router.get(path="/")
async def get_leaderboard_types() -> list[str]:
    return [leaderboard_type.name for leaderboard_type in LeaderboardTypes]
