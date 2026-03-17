"""Middlewares to include in routes for auto authorisation."""

from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from pydantic import BaseModel

from internal.auth.security import check_password
from internal.database.dependency import database_dependency
from internal.queries.admin import AsyncQuerier as AdminQuerier
from internal.queries.models import UserRole
from internal.queries.token import AsyncQuerier as TokenQuerier
from internal.queries.token import GetSessionByTokenRow
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.settings.env import auth_settings


class BasicAuthResponse(BaseModel):
    """Response when user got authorised with email and password."""

    user_id: int
    role: UserRole


async def basic_auth(
    conn: database_dependency, credentials: HTTPBasicCredentials = Security(HTTPBasic())
) -> BasicAuthResponse:
    """Fetches user id for endpoint with basic auth.

    Args:
      conn: database connection
      credentials: credentials (email(username), password) passed from request header

    Returns:
      user id and role if user authenticated

    Raises:
        HTTPException: if user wasn't found in the database or password incorrect
    """
    user = await UserQuerier(conn).get_user_login(email=credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not check_password(credentials.password, user.pw_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if user.role == UserRole.ADMIN:
        admin_info = await AdminQuerier(conn).get_admin(user_id=user.user_id)
        if admin_info and not admin_info.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account deactivated",
            )

    return BasicAuthResponse(user_id=user.user_id, role=user.role)


async def bearer_auth(
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
      HTTPException: if user wasn't found in the database
    """
    session = await TokenQuerier(conn).get_session_by_token(
        token=credentials.credentials
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        )
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
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised as consumer"
    )


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
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised as seller"
    )


async def admin_auth(
    conn: database_dependency, session: GetSessionByTokenRow = Security(bearer_auth)
) -> GetSessionByTokenRow:
    """Authentisate admin in a middleware.

    Args:
      conn: database connection
      session: user session from bearer authentication

    Returns:
      user session if user was successfully authenticated

    Raises:
      HTTPException: if user is not a admin
    """
    if session.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised as admin"
        )

    admin_info = await AdminQuerier(conn).get_admin(user_id=session.user_id)
    if not admin_info or not admin_info.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin account deactivated"
        )

    return session


def root_auth(credentials: HTTPBasicCredentials = Security(HTTPBasic())) -> None:
    """Root user authentication.

    Args:
        credentials: root user credentials

    Raises:
        HTTPException: if not root user
    """
    if ("" in {auth_settings.root_username, auth_settings.root_password}) or not (
        credentials.username == auth_settings.root_username
        and credentials.password == auth_settings.root_password
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Not authorised as root admin"
        )


BasicAuthDep = Annotated[BasicAuthResponse, Security(basic_auth)]
BearerAuthDep = Annotated[GetSessionByTokenRow, Security(bearer_auth)]
ConsumerAuthDep = Annotated[GetSessionByTokenRow, Security(consumer_auth)]
SellerAuthDep = Annotated[GetSessionByTokenRow, Security(seller_auth)]
AdminAuthDep = Annotated[GetSessionByTokenRow, Security(admin_auth)]
RootAuthDep = Annotated[None, Security(root_auth)]
