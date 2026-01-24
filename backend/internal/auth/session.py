from fastapi import Security
from sqlalchemy.engine import Connection
from internal.queries.models import Token
from internal.queries.token import Querier as TokenQuerier, GetSessionByTokenRow
from internal.queries.user import Querier as UserQuerier 
from .security import generate_token, check_password
from datetime import datetime, timedelta, timezone
from internal.settings import auth_settings
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials, HTTPBearer
from internal.database import database_dependency

# create and insert token into database
def create_token(user_id: int, conn: Connection) -> Token:
    token =  TokenQuerier(conn).create_token(user_id=user_id, token=generate_token(), expires_at=datetime.now(timezone.utc) + timedelta(seconds=auth_settings.token_exparation))
    if not token:
        raise ValueError("Failed to create token")
    return token

# delete token from database
def delete_token(token: str, conn: Connection):
    deleted_token = TokenQuerier(conn).delete_token(token=token)
    if not deleted_token:
        raise ValueError("Failed to delete token")

# security middleware to identify user
http_basic = HTTPBasic()
def basic_auth(conn: database_dependency, credentials: HTTPBasicCredentials = Security(http_basic)) -> int:
    user = UserQuerier (conn).get_user_login(email=credentials.username)
    if not user:
        raise ValueError("No user was found")
    if not check_password(credentials.password, user.pw_hash):
        raise ValueError("No user was found")
    return user.user_id

# security middleware to identify session
http_bearer = HTTPBearer()
def bearer_auth(conn: database_dependency, credentials: HTTPAuthorizationCredentials = Security(http_bearer)) -> GetSessionByTokenRow:
    session = TokenQuerier(conn).get_session_by_token(token=credentials.credentials)
    if not session:
        raise ValueError("No user was found")
    return session
