"""Endpoints for users."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Security, status
from internal.auth.middleware import bearer_auth
from internal.auth.security import UpdatePasswordForm, update_pw
from internal.database.dependency import database_dependency
from internal.queries.admin_issue_reports import AsyncQuerier as AdminIssueReportsQuerier
from internal.queries.admin_issue_reports import CreateAdminIssueReportParams
from internal.queries.models import AdminIssueReport, AdminIssueType
from internal.queries.token import GetSessionByTokenRow
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.queries.user import UpdateUserEmailParams
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/users", tags=["users"])


class CreateAdminIssueReportForm(BaseModel):
    """Admin issue report creation form."""

    issue_type: AdminIssueType
    description: str


@router.post(
    "/me/reports/admin",
    status_code=status.HTTP_201_CREATED,
    summary="Create admin issue report",
    description="Creates a new admin issue report for the authenticated user.",
    tags=["reports"],
)
async def create_admin_issue_report(
    form: CreateAdminIssueReportForm,
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> AdminIssueReport:
    """Create admin issue report.

    Args:
        form: admin issue report creation form
        conn: database connection
        session: user session

    Returns:
        created admin issue report

    Raises:
        HTTPException: if failed to create admin issue report
    """
    report = await AdminIssueReportsQuerier(conn).create_admin_issue_report(
        CreateAdminIssueReportParams(
            user_id=session.user_id,
            issue_type=form.issue_type,
            description=form.description,
        )
    )
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin issue report",
        )
    return report


@router.patch(
    "/me/password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update password",
    description="Updates the password for the authenticated user.",
)
async def update_password(
    form: UpdatePasswordForm,
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
) -> None:
    """Update users password.

    Args:
      form: form for password change
      conn: database connection
      session: users session
    """
    _ = await update_pw(session.email, form, conn)


@router.patch(
    "/me/email",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update email",
    description="Updates the email address for the authenticated user.",
)
async def update_email(
    email: EmailStr,
    conn: database_dependency,
    session: Annotated[GetSessionByTokenRow, Security(bearer_auth)],
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
