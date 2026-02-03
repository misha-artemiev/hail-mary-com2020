"""Middlewares to include in routes for auto authorisation."""

from fastapi import HTTPException, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from pydantic import BaseModel

from internal.auth.security import check_password
from internal.database.dependency import database_dependency
from internal.queries.models import UserRole
from internal.queries.token import GetSessionByTokenRow
from internal.queries.token import Querier as TokenQuerier
from internal.queries.user import Querier as UserQuerier


class BasicAuthResponse(BaseModel):
    """Response when user got authorised with email and password."""

    user_id: int
    role: UserRole


def basic_auth(
    conn: database_dependency, credentials: HTTPBasicCredentials = Security(HTTPBasic())
) -> BasicAuthResponse:
    """Fetches user id for endpoint with basic auth.

    Args:
      conn: database connection
      credentials: credentials (email(username), password) passed from request header

    Returns:
      user id and role if user authenticated

    Raises:
        ValueError: if user wasn't found in the database
    """
    user = UserQuerier(conn).get_user_login(email=credentials.username)
    if not user:
        raise ValueError("No user was found")
    if not check_password(credentials.password, user.pw_hash):
        raise ValueError("No user was found")
    return BasicAuthResponse(user_id=user.user_id, role=user.role)


def bearer_auth(
    conn: database_dependency,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> GetSessionByTokenRow:
    """Fetches user session from given token credentials.

    Args:
      conn: database connectionn
      credentials: credentials (token) gotten from headers

    Returns:
      user session with user and session information

    Raises:
      ValueError: if user wasn't found in the database
    """
    session = TokenQuerier(conn).get_session_by_token(token=credentials.credentials)
    if not session:
        raise ValueError("No user was found")
    return session


def consumer_auth(
    session: GetSessionByTokenRow = Security(bearer_auth),
) -> GetSessionByTokenRow:
    """Authentisate consumer in a middleware.

    Args:
      session: user session from bearer authentication

    Returns:
      user session if user was successfully authenticated

    Raises:
      HTTPException: if user is not a consumer
    """
    if session.role == UserRole.CONSUMER:
        return session
    raise HTTPException(401, "Not authorised as consumer")


def seller_auth(
    session: GetSessionByTokenRow = Security(bearer_auth),
) -> GetSessionByTokenRow:
    """Authentisate seller in a middleware.

    Args:
      session: user session from bearer authentication

    Returns:
      user session if user was successfully authenticated

    Raises:
      HTTPException: if user is not a seller
    """
    if session.role == UserRole.SELLER:
        return session
    raise HTTPException(401, "Not authorised as seller")


def admin_auth(
    session: GetSessionByTokenRow = Security(bearer_auth),
) -> GetSessionByTokenRow:
    """Authentisate admin in a middleware.

    Args:
      session: user session from bearer authentication

    Returns:
      user session if user was successfully authenticated

    Raises:
      HTTPException: if user is not a admin
    """
    if session.role == UserRole.ADMIN:
        return session
    raise HTTPException(401, "Not authorised as admin")
