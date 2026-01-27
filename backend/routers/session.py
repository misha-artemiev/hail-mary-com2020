"""Endpoint for session."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Response, Security
from internal.auth import basic_auth, bearer_auth, create_token, delete_token
from internal.auth.middleware import BasicAuthResponse
from internal.database import database_dependency
from internal.queries.models import UserRole
from internal.queries.token import GetSessionByTokenRow
from pydantic import BaseModel

router = APIRouter(prefix="/session", tags=["session"])


class TokenResponseModel(BaseModel):
    """Response on session creation."""

    token: str
    expires_at: datetime
    role: UserRole


@router.post("", response_model=TokenResponseModel, status_code=201)
def create_session(
    conn: database_dependency, user: Annotated[BasicAuthResponse, Security(basic_auth)]
) -> TokenResponseModel:
    """Create session if user exists.

    Args:
      conn: database connection
      user: user information if authorised

    Returns:
      user session information
    """
    token = create_token(user.user_id, conn)
    return TokenResponseModel(
        token=token.token, expires_at=token.expires_at, role=user.role
    )


@router.delete("", status_code=200)
def delete_session(
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> Response:
    """Delete session from database.

    Args:
      conn: database connection
      session: authorised users information

    Returns:
      when user session was deleted
    """
    delete_token(session.token, conn)
    return Response("Session was deleted", 200)
