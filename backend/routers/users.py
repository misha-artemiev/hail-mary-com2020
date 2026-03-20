"""Endpoints for users."""

from fastapi import APIRouter, HTTPException, Response, UploadFile, status
from internal.auth.middleware import BearerAuthDep
from internal.auth.security import UpdatePasswordForm, update_pw
from internal.block.management import block_management
from internal.database.dependency import database_dependency
from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams
from internal.queries.models import Inbox, UserRole
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.queries.user import UpdateUserEmailParams
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/users", tags=["users"])


class SendMessageForm(BaseModel):
    """Form to send a new message."""

    user_id: int
    message_subject: str
    message_text: str


@router.patch(
    "/me/password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update password",
    description="Updates the password for the authenticated user.",
)
async def update_password(
    form: UpdatePasswordForm, conn: database_dependency, session: BearerAuthDep
) -> None:
    """Update users password.

    Args:
      form: form for password change
      conn: database connection
      session: users session
    """
    await update_pw(session.email, form, conn)


@router.patch(
    "/me/email",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update email",
    description="Updates the email address for the authenticated user.",
)
async def update_email(
    email: EmailStr, conn: database_dependency, session: BearerAuthDep
) -> None:
    """Update users email.

    Args:
      email: new users email
      conn: database connection
      session: users session

    Raises:
      HTTPException: failed to update user email
    """
    user = await UserQuerier(conn).update_user_email(
        UpdateUserEmailParams(user_id=session.user_id, email=email)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update users email",
        )


@router.get(
    "/me/inbox",
    status_code=status.HTTP_200_OK,
    summary="Get user inbox",
    description="Gets all inbox messages for the authenticated user.",
    response_model=list[Inbox],
)
async def get_inbox(conn: database_dependency, session: BearerAuthDep) -> list[Inbox]:
    """Get inbox for user.

    Args:
      conn: database connection
      session: users session

    Returns:
      A list of inbox messages.
    """
    return [
        msg async for msg in InboxQuerier(conn).get_user_inbox(user_id=session.user_id)
    ]


@router.post(
    "/me/inbox",
    status_code=status.HTTP_201_CREATED,
    summary="Send an inbox message",
    description="Sends a new message to a user.",
    response_model=Inbox,
)
async def send_message(
    form: SendMessageForm, conn: database_dependency, session: BearerAuthDep
) -> Inbox:
    """Send a message.

    Args:
      form: The message form
      conn: database connection
      session: users session

    Returns:
      The created message.

    Raises:
      HTTPException: if message sending fails
    """
    message = await InboxQuerier(conn).create_inbox_message(
        CreateInboxMessageParams(
            user_id=form.user_id,
            sender_id=session.user_id,
            message_subject=form.message_subject,
            message_text=form.message_text,
        )
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )
    return message


@router.get(
    path="/id/{username}",
    summary="Get user ID by username",
    description="Retrieves a user ID and role by their username.",
)
async def get_user_id(username: str, conn: database_dependency) -> tuple[int, UserRole]:
    """Get user id from username.

    Args:
        username: username
        conn: database connection

    Returns:
        user id and role

    Raises:
        HTTPException: if failed to find user
    """
    if (user := await UserQuerier(conn).get_user_id(username=username)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "failed to find user")
    return (user.user_id, user.role)


@router.patch(
    path="/me/image",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Change profile image",
    description="Updates the profile image for the authenticated user.",
)
async def change_profile_image(file: UploadFile, session: BearerAuthDep) -> None:
    """Change user profile image.

    Args:
        file: profile image
        session: user session
    """
    await block_management.upload_profile_image(session.user_id, file)


@router.get(
    path="/{user_id}/image",
    status_code=status.HTTP_200_OK,
    summary="Get user profile image",
    description="Retrieves the profile image for a specific user by their ID.",
)
async def get_profile_image_by_id(user_id: int) -> Response:
    """Get user profile image by ID.

    Args:
        user_id: user id

    Returns:
        user profile image
    """
    return Response(
        block_management.get_profile_image(user_id), media_type="image/jpeg"
    )


@router.get(
    path="/me/image",
    status_code=status.HTTP_200_OK,
    summary="Get own profile image",
    description="Retrieves the profile image for the authenticated user.",
)
async def get_profile_image_me(session: BearerAuthDep) -> Response:
    """Get own profile image.

    Args:
        session: user session

    Returns:
        user profile image
    """
    return Response(
        block_management.get_profile_image(session.user_id), media_type="image/jpeg"
    )
