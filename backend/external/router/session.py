from internal.auth import create_token, delete_token, basic_auth, bearer_auth
from internal.database import database_dependency
from internal.queries.token import GetSessionByTokenRow
from fastapi import APIRouter, Response, Security

router = APIRouter(prefix="/consumers", tags=["consumers"])

@router.post("")
def create_session(conn: database_dependency, user_id: int = Security(basic_auth)):
    token = create_token(user_id, conn)
    return Response({"access_token": token.token, "expires_at": token.expires_at}, 200)

@router.delete("")
def delete_session(conn: database_dependency, session: GetSessionByTokenRow = Security(bearer_auth)):
    _ = delete_token(session.token, conn)
    return Response("Session was deleted", 200)
