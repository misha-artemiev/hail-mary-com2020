"""Sensitive information manimulation."""

import asyncio
import json
from secrets import choice, token_urlsafe

from bcrypt import checkpw, gensalt, hashpw
from fastapi import HTTPException, Request, status
from pydantic import BaseModel, SecretStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from internal.database.manager import database_manager
from internal.logger.logger import logger
from internal.queries.activity_log import AsyncQuerier as ActivityLogQuerier
from internal.queries.activity_log import CreateActivityLogParams
from internal.queries.models import UserRole
from internal.queries.token import AsyncQuerier as TokenQuerier
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.queries.user import UpdateUserPasswordParams, UpdateUserPasswordRow

SENSITIVE_FIELDS = {
    "password",
    "pw_hash",
    "token",
    "claim_code",
    "email",
    "new_password",
}


class LogData(BaseModel):
    """Data for activity log."""

    user_id: int | None
    user_role: UserRole | None
    method: str
    path: str
    query_params: dict[str, str]
    ip_address: str | None
    body: dict[str, object] | None


def sanitize_body(body: dict[str, object]) -> dict[str, object]:
    """Redact sensitive fields from request body.

    Returns:
        Body dict with sensitive fields redacted.
    """
    result: dict[str, object] = {}
    for key, value in body.items():
        if key.lower() in SENSITIVE_FIELDS:
            result[key] = "REDACTED"
        else:
            result[key] = value
    return result


async def get_user_from_token(token: str) -> tuple[int, UserRole] | tuple[None, None]:
    """Get user_id and role from Bearer token.

    Returns:
        Tuple of (user_id, user_role) or (None, None) if not found.
    """
    try:
        async for conn in database_manager.get_connection():
            session = await TokenQuerier(conn).get_session_by_token(token=token)
            if session:
                return session.user_id, session.role
    except SQLAlchemyError:
        logger.exception("Database error fetching user from token")
    return None, None


async def log_to_db(log_data: LogData) -> None:
    """Log activity to database."""
    details: str | None = None
    if log_data.body:
        details = json.dumps({"body": log_data.body})

    try:
        async for conn in database_manager.get_connection():
            await ActivityLogQuerier(conn).create_activity_log(
                CreateActivityLogParams(
                    user_id=log_data.user_id,
                    user_role=log_data.user_role,
                    action=f"{log_data.method} {log_data.path}",
                    resource_type=None,
                    resource_id=None,
                    details=details,
                    ip_address=log_data.ip_address,
                )
            )
            await conn.commit()
    except SQLAlchemyError:
        logger.exception("Failed to log to database")
        return


async def log_request(request: Request) -> None:
    """Log request details to activity_log table."""
    body = None
    content_type = request.headers.get("content-type", "")
    if (
        request.method in {"POST", "PATCH", "PUT"}
        and "application/json" in content_type
    ):
        try:
            raw_body = await request.json()
            if isinstance(raw_body, dict):
                body = sanitize_body(raw_body)
        except json.JSONDecodeError, KeyError:
            pass  # No body or invalid JSON - expected for some requests

    user_id: int | None = None
    user_role: UserRole | None = None
    auth_header = request.headers.get("authorization")
    is_bearer = auth_header is not None and auth_header.startswith("Bearer ")
    if is_bearer:
        auth_values = auth_header
        if auth_values is None:
            logger.exception("Failed to read the auth header.")
            return
        token = auth_values[7:]
        result = await get_user_from_token(token)
        user_id, user_role = result

    should_log = user_id or not is_bearer
    if should_log:
        log_data = LogData(
            user_id=user_id,
            user_role=user_role,
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            ip_address=request.client.host if request.client else None,
            body=body,
        )
        await log_to_db(log_data)


def hash_password(password: str) -> str:
    """Secure password hashing.

    Args:
      password: plain text password

    Returns:
      hashed password with salt
    """
    pasword_bytes = password.encode("utf-8")
    salt = gensalt(rounds=12)
    return hashpw(pasword_bytes, salt).decode("utf-8")


# check password against the hash
def check_password(password: str, password_hash: str) -> bool:
    """Checks if password corresponds with given password hash.

    Args:
      password: plain text password
      password_hash: hash that password gets check against

    Returns:
      if password is corresponds to a password hash
    """
    password_bytes = password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return checkpw(password_bytes, password_hash_bytes)


# generate url safe 256 bits
def generate_token() -> str:
    """Generates secure token for use anywhere on web.

    Returns:
      rendomly generated token as a string
    """
    return token_urlsafe(32)


class UpdatePasswordForm(BaseModel):
    """User form to update password."""

    old_password: SecretStr
    new_password: SecretStr


async def update_pw(
    email: str, form: UpdatePasswordForm, conn: AsyncConnection
) -> UpdateUserPasswordRow:
    """Update user password with old password check.

    Args:
      email: user email
      form: form with information to update password
      conn: database connection

    Returns:
      updated user record

    Raises:
      HTTPException: if failed to perform update
    """
    querier = UserQuerier(conn)
    user = await querier.get_user_login(email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find user",
        )
    is_valid = await asyncio.to_thread(
        check_password, form.old_password.get_secret_value(), user.pw_hash
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Old password is incorrect"
        )
    new_hashed_pw = await asyncio.to_thread(
        hash_password, form.new_password.get_secret_value()
    )
    user_updated = await querier.update_user_password(
        UpdateUserPasswordParams(user_id=user.user_id, pw_hash=new_hashed_pw)
    )
    if not user_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password",
        )
    return user_updated


def generate_claim_code(used_codes: list[str]) -> str:
    """Generate claim code.

    Args:
        used_codes: list of codes to avoid

    Returns:
        claim code
    """
    while True:
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        raw_code = "".join(choice(alphabet) for _ in range(4))
        code = f"{raw_code[:2]}-{raw_code[2:]}"
        if code not in used_codes:
            return code
