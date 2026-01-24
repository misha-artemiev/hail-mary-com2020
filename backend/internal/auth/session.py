from pydantic import EmailStr, SecretStr, BaseModel
from sqlalchemy.engine import Connection
from internal.queries.user import Querier as UserQuerier
from internal.queries.token import Querier as TokenQuerier, GetSessionByTokenRow
from internal.queries.models import Token
from .security import check_password, generate_token
from datetime import datetime, timedelta, timezone
from internal.settings import auth_settings

class CreateSessionForm(BaseModel):
    email: EmailStr
    password: SecretStr

def create_session(create_session_form: CreateSessionForm, conn: Connection) -> Token:
    user = UserQuerier(conn).get_user_for_login(email=create_session_form.email)
    if not user:
        raise ValueError("No user was found")
    if not check_password(create_session_form.password.get_secret_value(), user.pw_hash):
        raise ValueError("No user was found")
    token =  TokenQuerier(conn).create_token(user_id=user.user_id, token=generate_token(), expires_at=datetime.now(timezone.utc) + timedelta(seconds=auth_settings.token_exparation))
    if not token:
        raise ValueError("Failed to craete token")
    return token

class GetSession(BaseModel):
    token: str

def get_session_by_token(get_session_form: GetSession, conn: Connection) -> GetSessionByTokenRow:
    session = TokenQuerier(conn).get_session_by_token(token=get_session_form.token)
    if not session:
        raise ValueError("No user was found")
    return session

class DeleteSessionForm(BaseModel):
    token: str

def delete_session(delete_session_form: DeleteSessionForm, conn: Connection):
    deleted_token = TokenQuerier(conn).delete_token(token=delete_session_form.token)
    if not deleted_token:
        raise ValueError("Failed to delete token")
