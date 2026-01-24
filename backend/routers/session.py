from datetime import datetime
from pydantic import BaseModel, EmailStr
from internal.auth import create_token, delete_token, basic_auth, bearer_auth
from internal.database import database_dependency
from internal.queries.models import UserRole
from internal.queries.token import GetSessionByTokenRow
from fastapi import APIRouter, Security

router = APIRouter(prefix="/session", tags=["session"])

class TokenResponseModel(BaseModel):
    token: str
    expires_at: datetime

@router.post("", response_model=TokenResponseModel, status_code=201)
def create_session(conn: database_dependency, user_id: int = Security(basic_auth)):
    token = create_token(user_id, conn)
    return TokenResponseModel(token=token.token, expires_at=token.expires_at)

class SessionResponseModel(BaseModel):
    email: EmailStr
    role: UserRole
    token: str
    expires_at: datetime

@router.get("", response_model=SessionResponseModel, status_code=200)
def get_session(session: GetSessionByTokenRow = Security(bearer_auth)):
    return SessionResponseModel(
        email = session.email,
        role = session.role,
        token = session.token,
        expires_at = session.expires_at
    )

@router.delete("", status_code=200)
def delete_session(conn: database_dependency, session: GetSessionByTokenRow = Security(bearer_auth)):
    _ = delete_token(session.token, conn)
    return "Session was deleted"
