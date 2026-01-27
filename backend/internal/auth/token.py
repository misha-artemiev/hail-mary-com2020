"""Manages tokens in database."""

from datetime import UTC, datetime, timedelta

from internal.queries.models import Token
from internal.queries.token import CreateTokenParams
from internal.queries.token import Querier as TokenQuerier
from internal.settings import auth_settings
from sqlalchemy.engine import Connection

from .security import generate_token


def create_token(user_id: int, conn: Connection) -> Token:
    """Create, insert into database and return token for the user.

    Args:
      user_id: user id for which to create token
      conn: database connection

    Returns:
      row from the database for the created token

    Raises:
      ValueError: if database failed to insert token
    """
    token = TokenQuerier(conn).create_token(
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


def delete_token(token: str, conn: Connection) -> None:
    """Delete given token from database.

    Args:
      token: token to delete
      conn: database connection

    Raises:
      ValueError: if failed to delete or find given token
    """
    deleted_token = TokenQuerier(conn).delete_token(token=token)
    if not deleted_token:
        raise ValueError("Failed to delete token")
