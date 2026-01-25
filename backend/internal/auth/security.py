from bcrypt import hashpw, gensalt, checkpw
from secrets import token_urlsafe

# hash password, 12 rounds salt
def hash_password(password: str) -> str:
    pasword_bytes = password.encode("utf-8")
    salt = gensalt(rounds=12)
    return hashpw(pasword_bytes, salt).decode('utf-8')

# chack password against the hash
def check_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return checkpw(password_bytes, password_hash_bytes)

# generate url safe 256 bits
def generate_token() -> str:
    return token_urlsafe(32)
