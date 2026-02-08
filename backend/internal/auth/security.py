"""Sensitive information manimulation."""

from secrets import token_urlsafe, choice

from bcrypt import checkpw, gensalt, hashpw
from fastapi import HTTPException
from pydantic import BaseModel, SecretStr
from sqlalchemy import Connection

from internal.queries.user import Querier as UserQuerier
from internal.queries.user import UpdateUserPasswordParams, UpdateUserPasswordRow


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
      password_hash: hesh that password gets check against

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


def update_pw(
    email: str, form: UpdatePasswordForm, conn: Connection
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
    user = querier.get_user_login(email=email)
    if not user:
        raise HTTPException(500)
    if not check_password(form.old_password.get_secret_value(), user.pw_hash):
        raise HTTPException(403)
    user_updated = querier.update_user_password(
        UpdateUserPasswordParams(
            user_id=user.user_id,
            pw_hash=hash_password(form.new_password.get_secret_value()),
        )
    )
    if not user_updated:
        raise HTTPException(500)
    return user_updated

def generate_claim_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    code = ''.join(choice(alphabet) for _ in range(6))
    return code
