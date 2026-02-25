"""Manages tokens in database."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncConnection

from internal.queries.models import Token
from internal.queries.token import AsyncQuerier as TokenQuerier
from internal.queries.token import CreateTokenParams
from internal.settings.env import auth_settings

from .security import generate_token


async def create_token(user_id: int, conn: AsyncConnection) -> Token:
    """Create, insert into database and return token for the user.

    Args:
      user_id: user id for which to create token
      conn: database connection

    Returns:
      row from the database for the created token

    Raises:
      ValueError: if database failed to insert token
    """
    token = await TokenQuerier(conn).create_token(
        CreateTokenParams(
            user_id=user_id,
            token=generate_token(),
            expires_at=datetime.now(UTC)
            + timedelta(seconds=auth_settings.token_exparation),
        )
    )
    if not token:
        raise ValueError("Failed to create token")
    return token


async def delete_token(token: str, conn: AsyncConnection) -> None:
    """Delete given token from database.

    Args:
      token: token to delete
      conn: database connection

    Raises:
      ValueError: if failed to delete or find given token
    """
    deleted_token = await TokenQuerier(conn).delete_token(token=token)
    if not deleted_token:
        raise ValueError("Failed to delete token")
