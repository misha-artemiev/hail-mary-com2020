"""Endpoints for users."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Security, status
from internal.auth.middleware import bearer_auth
from internal.auth.security import UpdatePasswordForm, update_pw
from internal.database.dependency import database_dependency
from internal.queries.token import GetSessionByTokenRow
from internal.queries.user import Querier as UserQuerier
from internal.queries.user import UpdateUserEmailParams
from pydantic import EmailStr

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/password", status_code=202)
async def update_password(
    form: UpdatePasswordForm,
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> Response:
    """Update users password.

    Args:
      form: form for password change
      conn: database connection
      session: users session

    Returns:
      if password was changed
    """
    _ = update_pw(session.email, form, conn)
    return Response("Password was updated", 202)


@router.patch("/me/email", status_code=202)
async def update_email(
    email: EmailStr,
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> Response:
    """Update users email.

    Args:
      email: new users email
      conn: database connection
      session: users session

    Returns:
      if sellers email was updated

    Raises:
      HTTPException: failed to update user email
    """
    user = UserQuerier(conn).update_user_email(
        UpdateUserEmailParams(user_id=session.user_id, email=email)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update users email",
        )
    return Response("user email was updated", 201)
