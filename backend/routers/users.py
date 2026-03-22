"""Endpoints for users."""

from fastapi import APIRouter, HTTPException, Response, UploadFile, status
from internal.auth.middleware import BearerAuthDep
from internal.auth.security import UpdatePasswordForm, update_pw
from internal.block.management import block_management
from internal.database.dependency import database_dependency
from internal.inbox.notifications import send_notification
from internal.queries.admin_issue_reports import (
    AsyncQuerier as AdminIssueReportsQuerier,
)
from internal.queries.admin_issue_reports import CreateAdminIssueReportParams
from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams
from internal.queries.models import (
    AdminIssueReport,
    AdminIssueType,
    Inbox,
    SellerIssueReport,
    SellerIssueType,
    UserRole,
)
from internal.queries.reservations import AsyncQuerier as ReservationsQuerier
from internal.queries.seller_issue_reports import (
    AsyncQuerier as SellerIssueReportsQuerier,
)
from internal.queries.seller_issue_reports import CreateSellerIssueReportParams
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


@router.delete(
    "/me/inbox/{message_id}",
    status_code=status.HTTP_200_OK,
    summary="Dismiss an inbox message",
    description="Deletes a specific inbox message owned by the authenticated user.",
    response_model=Inbox,
)
async def dismiss_inbox_message(
    message_id: int, conn: database_dependency, session: BearerAuthDep
) -> Inbox:
    """Dismiss a single inbox message for the current user.

    Args:
      message_id: inbox message id
      conn: database connection
      session: users session

    Returns:
      The deleted inbox message.

    Raises:
      HTTPException: if message does not exist for user or delete fails
    """
    inbox_querier = InboxQuerier(conn)
    user_messages = [
        msg async for msg in inbox_querier.get_user_inbox(user_id=session.user_id)
    ]
    if all(msg.message_id != message_id for msg in user_messages):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inbox message not found"
        )

    deleted_message = await inbox_querier.delete_inbox_message(message_id=message_id)
    if not deleted_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss inbox message",
        )
    return deleted_message


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


class CreateSellerIssueReportForm(BaseModel):
    """Seller issue report creation form."""

    issue_type: SellerIssueType
    description: str


async def create_seller_issue_report(
    reservation_id: int,
    form: CreateSellerIssueReportForm,
    conn: database_dependency,
    user: BearerAuthDep,
) -> SellerIssueReport:
    """Create seller issue report.

    Args:
        reservation_id: reservation id from path
        form: seller issue report creation form
        conn: database connection
        user: user session

    Returns:
        created seller issue report

    Raises:
        HTTPException: if failed to create report or reservation not owned by consumer
    """
    reservation = await ReservationsQuerier(conn).get_reservation(
        reservation_id=reservation_id
    )
    if not reservation or reservation.consumer_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found or not owned by consumer",
        )

    report = await SellerIssueReportsQuerier(conn).create_seller_issue_report(
        CreateSellerIssueReportParams(
            reservation_id=reservation_id,
            issue_type=form.issue_type,
            description=form.description,
        )
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create seller issue report",
        )

    await send_notification(
        conn,
        user_id=user.user_id,
        sender_id=user.user_id,
        subject="Issue report submitted",
        text="Your reservation issue report was submitted successfully.",
    )

    return report


@router.post(
    "/me/reports/seller/{reservation_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Create seller issue report",
    description="Creates a seller issue report for a reservation owned by the user.",
    tags=["reports"],
)
async def create_seller_issue_report_endpoint(
    reservation_id: int,
    form: CreateSellerIssueReportForm,
    conn: database_dependency,
    user: BearerAuthDep,
) -> SellerIssueReport:
    """Create seller issue report endpoint wrapper.

    Returns:
        The created seller issue report.
    """
    return await create_seller_issue_report(
        reservation_id=reservation_id, form=form, conn=conn, user=user
    )


class CreateAdminIssueReportForm(BaseModel):
    """Admin issue report creation form."""

    issue_type: AdminIssueType
    description: str


@router.post(
    "/me/reports/admin",
    status_code=status.HTTP_201_CREATED,
    summary="Create admin issue report",
    description="Creates a new admin issue report.",
    tags=["reports"],
)
async def create_admin_issue_report(
    form: CreateAdminIssueReportForm, conn: database_dependency, user: BearerAuthDep
) -> AdminIssueReport:
    """Create admin issue report.

    Args:
        form: admin issue report creation form
        conn: database connection
        user: user session

    Returns:
        created admin issue report

    Raises:
        HTTPException: if failed to create report
    """
    report = await AdminIssueReportsQuerier(conn).create_admin_issue_report(
        CreateAdminIssueReportParams(
            user_id=user.user_id,
            issue_type=form.issue_type,
            description=form.description,
        )
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin issue report",
        )

    await send_notification(
        conn,
        user_id=user.user_id,
        sender_id=user.user_id,
        subject="Issue report submitted",
        text=("Your issue report was submitted successfully and is awaiting review."),
    )

    return report


@router.get(
    "/me/reports/admin",
    status_code=status.HTTP_200_OK,
    summary="Get admin issue reports",
    description="Retrieves a list of admin issue reports created by the user.",
    tags=["reports"],
)
async def get_admin_issue_reports(
    conn: database_dependency, user: BearerAuthDep
) -> list[AdminIssueReport]:
    """Get admin issue reports.

    Args:
        conn: database connection
        user: user session

    Returns:
        list of admin issue reports
    """
    return [
        r
        async for r in AdminIssueReportsQuerier(conn).get_admin_issue_reports_by_user(
            user_id=user.user_id
        )
    ]


@router.get(
    "/me/reports/seller",
    status_code=status.HTTP_200_OK,
    summary="Get seller issue reports",
    description="Retrieves a list of seller issue reports created by the user.",
    tags=["reports"],
)
async def get_seller_issue_reports(
    conn: database_dependency, user: BearerAuthDep
) -> list[SellerIssueReport]:
    """Get seller issue reports.

    Args:
        conn: database connection
        user: user session

    Returns:
        list of seller issue reports
    """
    return [
        r
        async for r in SellerIssueReportsQuerier(conn).get_seller_issue_reports_by_user(
            consumer_id=user.user_id
        )
    ]
