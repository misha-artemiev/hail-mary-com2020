"""Sensitive information manimulation."""

from secrets import token_urlsafe

from bcrypt import checkpw, gensalt, hashpw


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
