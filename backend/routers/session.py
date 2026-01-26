from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Response, Security
from internal.auth import basic_auth, bearer_auth, create_token, delete_token
from internal.database import database_dependency
from internal.queries.models import UserRole
from internal.queries.token import GetSessionByTokenRow
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/session", tags=["session"])


class TokenResponseModel(BaseModel):
    token: str
    expires_at: datetime


@router.post("", response_model=TokenResponseModel, status_code=201)
def create_session(
    conn: database_dependency, user_id: Annotated[int, Security(basic_auth)]
) -> TokenResponseModel:
    token = create_token(user_id, conn)
    return TokenResponseModel(token=token.token, expires_at=token.expires_at)


class SessionResponseModel(BaseModel):
    email: EmailStr
    role: UserRole
    token: str
    expires_at: datetime


@router.get("", response_model=SessionResponseModel, status_code=200)
def get_session(
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> SessionResponseModel:
    return SessionResponseModel(
        email=session.email,
        role=session.role,
        token=session.token,
        expires_at=session.expires_at,
    )


@router.delete("", status_code=200)
def delete_session(
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> Response:
    delete_token(session.token, conn)
    return Response("Session was deleted", 200)
