"""Middlewares to include in routes for auto authorisation"""

from fastapi import Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from internal.auth.security import check_password
from internal.database import database_dependency
from internal.queries.token import GetSessionByTokenRow
from internal.queries.token import Querier as TokenQuerier
from internal.queries.user import Querier as UserQuerier


def basic_auth(
    conn: database_dependency, credentials: HTTPBasicCredentials = Security(HTTPBasic())
) -> int:
    """Fetches user id for endpoint with basic auth

    Args:
      conn: database connection
      credentials: credentials passed from request header

    Returns:
      user id that corresponds with given credentials

    Raises:
    """
    user = UserQuerier(conn).get_user_login(email=credentials.username)
    if not user:
        raise ValueError("No user was found")
    if not check_password(credentials.password, user.pw_hash):
        raise ValueError("No user was found")
    return user.user_id


def bearer_auth(
    conn: database_dependency,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> GetSessionByTokenRow:
    session = TokenQuerier(conn).get_session_by_token(token=credentials.credentials)
    if not session:
        raise ValueError("No user was found")
    return session
