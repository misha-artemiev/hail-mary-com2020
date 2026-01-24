from datetime import datetime
from pydantic import BaseModel
from internal.auth import create_token, delete_token, basic_auth, bearer_auth
from internal.database import database_dependency
from internal.queries.token import GetSessionByTokenRow
from fastapi import APIRouter, Security

router = APIRouter(prefix="/session", tags=["session"])

class SessionResponseModel(BaseModel):
    token: str
    expires_at: datetime

@router.post("", response_model=SessionResponseModel, status_code=201)
def create_session(conn: database_dependency, user_id: int = Security(basic_auth)):
    token = create_token(user_id, conn)
    return SessionResponseModel(token=token.token, expires_at=token.expires_at)

@router.delete("", status_code=200)
def delete_session(conn: database_dependency, session: GetSessionByTokenRow = Security(bearer_auth)):
    _ = delete_token(session.token, conn)
    return "Session was deleted"
