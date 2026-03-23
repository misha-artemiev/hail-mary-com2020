"""Endpoints for admins."""

from fastapi import APIRouter, HTTPException, status
from internal.auth.creation import CreateAdminForm, create_admin
from internal.auth.middleware import AdminAuthDep, RootAuthDep
from internal.auth.security import hash_password
from internal.database.dependency import database_dependency
from internal.queries.admin import AsyncQuerier as AdminQuerier
from internal.queries.admin import (
    GetAdminRow,
    GetAdminsRow,
    SetIsAdminActiveParams,
    UpdateAdminParams,
)
from internal.queries.admin_issue_reports import (
    AsyncQuerier as AdminIssueReportsQuerier,
)
from internal.queries.admin_issue_reports import UpdateAdminIssueReportStatusParams
from internal.queries.allergens import AsyncQuerier as AllergensQuerier
from internal.queries.allergens import UpdateAllergenParams
from internal.queries.badge import AsyncQuerier as BadgeQuerier
from internal.queries.badge import UpdateBadgeParams
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.category import AsyncQuerier as CategoryQuerier
from internal.queries.category import CreateCategoryParams, UpdateCategoryParams
from internal.queries.consumer import AsyncQuerier as ConsumerQuerier
from internal.queries.consumer import GetConsumersRow, UpdateConsumerParams
from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams
from internal.queries.models import (
    Admin,
    AdminIssueReport,
    Allergen,
    Badge,
    Bundle,
    Category,
    Consumer,
    Inbox,
    IssueStatus,
    Reservation,
    Seller,
    SellerIssueReport,
)
from internal.queries.reservations import AsyncQuerier as ReservationsQuerier
from internal.queries.seller import AsyncQuerier as SellerQuerier
from internal.queries.seller import (
    GetSellersRow,
    UpdateSellerParams,
    VerifySellerParams,
)
from internal.queries.seller_issue_reports import (
    AsyncQuerier as SellerIssueReportsQuerier,
)
from internal.queries.seller_issue_reports import UpdateSellerIssueReportStatusParams
from internal.queries.user import AsyncQuerier as UserQuerier
from internal.queries.user import (
    DeleteUserRow,
    GetUsersRow,
    UpdateUserEmailParams,
    UpdateUserEmailRow,
    UpdateUserPasswordParams,
    UpdateUserPasswordRow,
)
from pydantic import BaseModel, SecretStr

router = APIRouter(prefix="/admins", tags=["admins"])


class UpdateAdminForm(BaseModel):
    """Admin name update form."""

    first_name: str
    last_name: str


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create admin",
    description="Create admin by root user",
    tags=["root admin"],
)
async def register_admin(
    form: CreateAdminForm, conn: database_dependency, _: RootAuthDep
) -> None:
    """Create admin by root user.

    Args:
        form: new admin information
        conn: database connection
    """
    await create_admin(form, conn)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get all admins",
    description="Retrieves a list of all registered admins by root user.",
    tags=["root admin"],
)
async def get_admins(conn: database_dependency, _: RootAuthDep) -> list[GetAdminsRow]:
    """Get all admins by root user.

    Args:
        conn: database connection

    Returns:
        list of all admins
    """
    return [admin_row async for admin_row in AdminQuerier(conn).get_admins()]


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get authenticated admin",
    description="Retrieves the profile of the authenticated admin.",
)
async def get_admin_me(
    conn: database_dependency, admin_session: AdminAuthDep
) -> GetAdminRow:
    """Get authenticated admin profile.

    Args:
        conn: database connection
        admin_session: admin session

    Returns:
        admin profile

    Raises:
        HTTPException: if admin not found
    """
    admin_profile = await AdminQuerier(conn).get_admin(user_id=admin_session.user_id)
    if not admin_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin profile not found"
        )
    return admin_profile


@router.get(
    "/{admin_id}",
    status_code=status.HTTP_200_OK,
    summary="Get admin by ID",
    description="Retrieves the profile of an admin by their unique ID by root user.",
    tags=["root admin"],
)
async def get_admin_by_id(
    admin_id: int, conn: database_dependency, _: RootAuthDep
) -> GetAdminRow:
    """Get admin profile by ID by root user.

    Args:
        admin_id: unique identifier of the admin
        conn: database connection

    Returns:
        admin profile

    Raises:
        HTTPException: if admin not found
    """
    admin_profile = await AdminQuerier(conn).get_admin(user_id=admin_id)
    if not admin_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found"
        )
    return admin_profile


@router.patch(
    "/{admin_id}",
    status_code=status.HTTP_200_OK,
    summary="Update admin profile",
    description="Updates the profile information for an admin by root user.",
    tags=["root admin"],
)
async def update_admin(
    admin_id: int, form: UpdateAdminForm, conn: database_dependency, _: RootAuthDep
) -> Admin:
    """Admin name update by root user.

    Args:
        admin_id: admin id
        form: admin update form
        conn: database connection

    Returns:
        updated admin

    Raises:
        HTTPException: if failed to update admin
    """
    updated_admin_profile = await AdminQuerier(conn).update_admin(
        UpdateAdminParams(user_id=admin_id, fname=form.first_name, lname=form.last_name)
    )
    if not updated_admin_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update admin",
        )
    return updated_admin_profile


@router.patch(
    "/{admin_id}/deactivate",
    status_code=status.HTTP_200_OK,
    summary="Deactivate admin",
    description="Deactivate admin by root user",
    tags=["root admin"],
)
async def deactivate_admin(
    admin_id: int, conn: database_dependency, _: RootAuthDep
) -> Admin:
    """Deactivate admin.

    Args:
        admin_id: admin id
        conn: database connection

    Returns:
        deactivated admin

    Raises:
        HTTPException: if failed to find admin
    """
    admin_deactivation_result = await AdminQuerier(conn).set_is_admin_active(
        SetIsAdminActiveParams(user_id=admin_id, active=False)
    )
    if not admin_deactivation_result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No admin was found")
    return admin_deactivation_result


@router.patch(
    "/{admin_id}/activate",
    status_code=status.HTTP_200_OK,
    summary="Activate admin",
    description="Activate admin by root user",
    tags=["root admin"],
)
async def activate_admin(
    admin_id: int, conn: database_dependency, _: RootAuthDep
) -> Admin:
    """Activate admin.

    Args:
        admin_id: admin id
        conn: database connection

    Returns:
        activated admin

    Raises:
        HTTPException: if failed to find admin
    """
    admin_activation_result = await AdminQuerier(conn).set_is_admin_active(
        SetIsAdminActiveParams(user_id=admin_id, active=True)
    )
    if not admin_activation_result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No admin was found")
    return admin_activation_result


@router.get(
    "/database/users",
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Retrieves a list of all users in the system.",
)
async def get_all_users(
    conn: database_dependency, _: AdminAuthDep
) -> list[GetUsersRow]:
    """Get all users.

    Args:
        conn: database connection

    Returns:
        list of all users
    """
    return [user_row async for user_row in UserQuerier(conn).get_users()]


class UpdateUserEmailForm(BaseModel):
    """User email update form."""

    email: str


@router.patch(
    "/database/users/{user_id}/email",
    status_code=status.HTTP_200_OK,
    summary="Update user email",
    description="Updates the email address for a specific user.",
)
async def update_user_email(
    user_id: int, form: UpdateUserEmailForm, conn: database_dependency, _: AdminAuthDep
) -> UpdateUserEmailRow:
    """Update user email.

    Args:
        user_id: user id
        form: email update form
        conn: database connection

    Returns:
        updated user record

    Raises:
        HTTPException: if failed to update email
    """
    updated_user_email = await UserQuerier(conn).update_user_email(
        UpdateUserEmailParams(user_id=user_id, email=form.email)
    )
    if not updated_user_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return updated_user_email


class UpdateUserPasswordForm(BaseModel):
    """User password update form."""

    password: SecretStr


@router.patch(
    "/database/users/{user_id}/password",
    status_code=status.HTTP_200_OK,
    summary="Update user password",
    description="Updates the password for a specific user.",
)
async def update_user_password(
    user_id: int,
    form: UpdateUserPasswordForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> UpdateUserPasswordRow:
    """Update user password.

    Args:
        user_id: user id
        form: password update form
        conn: database connection

    Returns:
        updated user record

    Raises:
        HTTPException: if failed to update password
    """
    hashed_pw = hash_password(form.password.get_secret_value())
    updated_user_password = await UserQuerier(conn).update_user_password(
        UpdateUserPasswordParams(user_id=user_id, pw_hash=hashed_pw)
    )
    if not updated_user_password:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return updated_user_password


@router.delete(
    "/database/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Deletes a specific user from the system.",
)
async def delete_user(
    user_id: int, conn: database_dependency, _: AdminAuthDep
) -> DeleteUserRow:
    """Delete user.

    Args:
        user_id: user id
        conn: database connection

    Returns:
        deleted user

    Raises:
        HTTPException: if user not found
    """
    deleted_user = await UserQuerier(conn).delete_user(user_id=user_id)
    if not deleted_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return deleted_user


@router.get(
    "/database/sellers",
    status_code=status.HTTP_200_OK,
    summary="Get all sellers",
    description="Retrieves a list of all sellers in the system.",
)
async def get_all_sellers(
    conn: database_dependency, _: AdminAuthDep
) -> list[GetSellersRow]:
    """Get all sellers.

    Args:
        conn: database connection

    Returns:
        list of all sellers
    """
    return [seller_row async for seller_row in SellerQuerier(conn).get_sellers()]


@router.patch(
    "/database/sellers/{seller_id}/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify seller",
    description="Verifies a seller. Only possible if coordinates exist.",
)
async def verify_seller(
    seller_id: int, conn: database_dependency, admin_session: AdminAuthDep
) -> Seller:
    """Verify seller. Only possible if coordinates exist.

    Args:
        seller_id: seller id
        conn: database connection
        admin_session: admin session

    Returns:
        verified seller

    Raises:
        HTTPException: if seller not found or coordinates missing
    """
    seller_querier = SellerQuerier(conn)
    seller_profile = await seller_querier.get_seller(user_id=seller_id)
    if not seller_profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller not found")

    if seller_profile.latitude is None or seller_profile.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot verify seller without valid coordinates",
        )

    verified_seller_profile = await seller_querier.verify_seller(
        VerifySellerParams(user_id=seller_id, verified_by=admin_session.user_id)
    )
    if not verified_seller_profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller not found")
    return verified_seller_profile


@router.patch(
    "/database/sellers/{seller_id}/unverify",
    status_code=status.HTTP_200_OK,
    summary="Unverify seller",
    description="Removes verification status from a seller.",
)
async def unverify_seller(
    seller_id: int, conn: database_dependency, _: AdminAuthDep
) -> Seller:
    """Unverify seller.

    Args:
        seller_id: seller id
        conn: database connection

    Returns:
        unverified seller

    Raises:
        HTTPException: if seller not found
    """
    unverified_seller_profile = await SellerQuerier(conn).unverify_seller(
        user_id=seller_id
    )
    if not unverified_seller_profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller not found")
    return unverified_seller_profile


class UpdateSellerForm(BaseModel):
    """Seller profile update form."""

    seller_name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    post_code: str
    region: str | None = None
    country: str
    latitude: float | None = None
    longitude: float | None = None


@router.patch(
    "/database/sellers/{seller_id}",
    status_code=status.HTTP_200_OK,
    summary="Update seller profile",
    description="Updates the profile information for a specific seller.",
)
async def update_seller_profile(
    seller_id: int, form: UpdateSellerForm, conn: database_dependency, _: AdminAuthDep
) -> Seller:
    """Update seller profile.

    Args:
        seller_id: seller id
        form: seller update form
        conn: database connection

    Returns:
        updated seller

    Raises:
        HTTPException: if seller not found or invalid coordinate update
    """
    seller_querier = SellerQuerier(conn)
    current_seller = await seller_querier.get_seller(user_id=seller_id)
    if not current_seller:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller not found")

    if current_seller.verified_by is not None and (
        form.latitude is None or form.longitude is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove coordinates from a verified seller. "
            "Unverify them first.",
        )

    updated_seller_profile = await seller_querier.update_seller(
        UpdateSellerParams(
            user_id=seller_id,
            seller_name=form.seller_name,
            address_line1=form.address_line1,
            address_line2=form.address_line2,
            city=form.city,
            post_code=form.post_code,
            region=form.region,
            country=form.country,
            latitude=form.latitude,
            longitude=form.longitude,
        )
    )
    if not updated_seller_profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Seller not found")
    return updated_seller_profile


@router.get(
    "/database/consumers",
    status_code=status.HTTP_200_OK,
    summary="Get all consumers",
    description="Retrieves a list of all consumers in the system.",
)
async def get_all_consumers(
    conn: database_dependency, _: AdminAuthDep
) -> list[GetConsumersRow]:
    """Get all consumers.

    Args:
        conn: database connection

    Returns:
        list of all consumers
    """
    return [
        consumer_row async for consumer_row in ConsumerQuerier(conn).get_consumers()
    ]


class UpdateConsumerForm(BaseModel):
    """Consumer profile update form."""

    first_name: str
    last_name: str


@router.patch(
    "/database/consumers/{consumer_id}",
    status_code=status.HTTP_200_OK,
    summary="Update consumer profile",
    description="Updates the profile information for a specific consumer.",
)
async def update_consumer_profile(
    consumer_id: int,
    form: UpdateConsumerForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> Consumer:
    """Update consumer profile.

    Args:
        consumer_id: consumer id
        form: consumer update form
        conn: database connection

    Returns:
        updated consumer

    Raises:
        HTTPException: if consumer not found
    """
    updated_consumer_profile = await ConsumerQuerier(conn).update_consumer(
        UpdateConsumerParams(
            user_id=consumer_id, fname=form.first_name, lname=form.last_name
        )
    )
    if not updated_consumer_profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consumer not found")
    return updated_consumer_profile


@router.get(
    "/database/bundles",
    status_code=status.HTTP_200_OK,
    summary="Get all bundles",
    description="Retrieves a list of all bundles in the system.",
)
async def get_all_bundles(conn: database_dependency, _: AdminAuthDep) -> list[Bundle]:
    """Get all bundles.

    Args:
        conn: database connection

    Returns:
        list of all bundles
    """
    return [bundle_row async for bundle_row in BundleQuerier(conn).get_bundles()]


@router.delete(
    "/database/bundles/{bundle_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete bundle",
    description="Deletes a specific bundle from the system.",
)
async def delete_bundle(
    bundle_id: int, conn: database_dependency, _: AdminAuthDep
) -> Bundle:
    """Delete bundle.

    Args:
        bundle_id: bundle id
        conn: database connection

    Returns:
        deleted bundle

    Raises:
        HTTPException: if bundle not found
    """
    deleted_bundle = await BundleQuerier(conn).delete_bundle(bundle_id=bundle_id)
    if not deleted_bundle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bundle not found")
    return deleted_bundle


@router.get(
    "/database/reservations",
    status_code=status.HTTP_200_OK,
    summary="Get all reservations",
    description="Retrieves a list of all reservations in the system.",
)
async def get_all_reservations(
    conn: database_dependency, _: AdminAuthDep
) -> list[Reservation]:
    """Get all reservations.

    Args:
        conn: database connection

    Returns:
        list of all reservations
    """
    return [
        reservation_row
        async for reservation_row in ReservationsQuerier(conn).get_reservations()
    ]


@router.delete(
    "/database/reservations/{reservation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete reservation",
    description="Deletes a specific reservation from the system.",
)
async def delete_reservation(
    reservation_id: int, conn: database_dependency, _: AdminAuthDep
) -> Reservation:
    """Delete reservation.

    Args:
        reservation_id: reservation id
        conn: database connection

    Returns:
        deleted reservation

    Raises:
        HTTPException: if reservation not found
    """
    deleted_reservation = await ReservationsQuerier(conn).delete_reservation(
        reservation_id=reservation_id
    )
    if not deleted_reservation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    return deleted_reservation


@router.get(
    "/database/allergens",
    status_code=status.HTTP_200_OK,
    summary="Get all allergens",
    description="Retrieves a list of all allergens in the system.",
)
async def get_all_allergens(
    conn: database_dependency, _: AdminAuthDep
) -> list[Allergen]:
    """Get all allergens.

    Args:
        conn: database connection

    Returns:
        list of all allergens
    """
    return [
        allergen_row async for allergen_row in AllergensQuerier(conn).get_allergens()
    ]


class CreateAllergenForm(BaseModel):
    """Allergen creation form."""

    allergen_name: str


@router.post(
    "/database/allergens",
    status_code=status.HTTP_201_CREATED,
    summary="Create allergen",
    description="Creates a new allergen in the system.",
)
async def create_allergen(
    form: CreateAllergenForm, conn: database_dependency, _: AdminAuthDep
) -> Allergen:
    """Create allergen.

    Args:
        form: form with the name of the allergen
        conn: database connection

    Returns:
        created allergen

    Raises:
        HTTPException: if failed to create allergen
    """
    created_allergen = await AllergensQuerier(conn).create_allergen(
        allergen_name=form.allergen_name
    )
    if not created_allergen:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create allergen"
        )
    return created_allergen


class UpdateAllergenForm(BaseModel):
    """Allergen update form."""

    allergen_name: str


@router.patch(
    "/database/allergens/{allergen_id}",
    status_code=status.HTTP_200_OK,
    summary="Update allergen",
    description="Updates the name of a specific allergen.",
)
async def update_allergen(
    allergen_id: int,
    form: UpdateAllergenForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> Allergen:
    """Update allergen.

    Args:
        allergen_id: allergen id
        form: form with the new name of the allergen
        conn: database connection

    Returns:
        updated allergen

    Raises:
        HTTPException: if allergen not found
    """
    updated_allergen = await AllergensQuerier(conn).update_allergen(
        UpdateAllergenParams(allergen_id=allergen_id, allergen_name=form.allergen_name)
    )
    if not updated_allergen:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Allergen not found")
    return updated_allergen


@router.delete(
    "/database/allergens/{allergen_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete allergen",
    description="Deletes a specific allergen from the system.",
)
async def delete_allergen(
    allergen_id: int, conn: database_dependency, _: AdminAuthDep
) -> Allergen:
    """Delete allergen.

    Args:
        allergen_id: allergen id
        conn: database connection

    Returns:
        deleted allergen

    Raises:
        HTTPException: if allergen not found
    """
    deleted_allergen = await AllergensQuerier(conn).delete_allergen(
        allergen_id=allergen_id
    )
    if not deleted_allergen:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Allergen not found")
    return deleted_allergen


@router.get(
    "/database/categories",
    status_code=status.HTTP_200_OK,
    summary="Get all categories",
    description="Retrieves a list of all categories in the system.",
)
async def get_all_categories(
    conn: database_dependency, _: AdminAuthDep
) -> list[Category]:
    """Get all categories.

    Args:
        conn: database connection

    Returns:
        list of all categories
    """
    return [
        category_row async for category_row in CategoryQuerier(conn).get_categories()
    ]


class CreateCategoryForm(BaseModel):
    """Category creation form."""

    category_name: str
    category_coefficient: float


@router.post(
    "/database/categories",
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Creates a new category in the system.",
)
async def create_category(
    form: CreateCategoryForm, conn: database_dependency, _: AdminAuthDep
) -> Category:
    """Create category.

    Args:
        form: category creation form
        conn: database connection

    Returns:
        created category

    Raises:
        HTTPException: if failed to create category
    """
    created_category = await CategoryQuerier(conn).create_category(
        CreateCategoryParams(
            category_name=form.category_name,
            category_coefficient=form.category_coefficient,
        )
    )
    if not created_category:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create category"
        )
    return created_category


@router.patch(
    "/database/categories/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Update category",
    description="Updates the name and coefficient of a specific category.",
)
async def update_category(
    category_id: int,
    form: CreateCategoryForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> Category:
    """Update category.

    Args:
        category_id: category id
        form: category update form
        conn: database connection

    Returns:
        updated category

    Raises:
        HTTPException: if category not found
    """
    updated_category = await CategoryQuerier(conn).update_category(
        UpdateCategoryParams(
            category_id=category_id,
            category_name=form.category_name,
            category_coefficient=form.category_coefficient,
        )
    )
    if not updated_category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return updated_category


@router.delete(
    "/database/categories/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete category",
    description="Deletes a specific category from the system.",
)
async def delete_category(
    category_id: int, conn: database_dependency, _: AdminAuthDep
) -> Category:
    """Delete category.

    Args:
        category_id: category id
        conn: database connection

    Returns:
        deleted category

    Raises:
        HTTPException: if category not found
    """
    deleted_category = await CategoryQuerier(conn).delete_category(
        category_id=category_id
    )
    if not deleted_category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return deleted_category


@router.get(
    "/database/badges",
    status_code=status.HTTP_200_OK,
    summary="Get all badges",
    description="Retrieves a list of all badges in the system.",
)
async def get_all_badges(conn: database_dependency, _: AdminAuthDep) -> list[Badge]:
    """Get all badges.

    Args:
        conn: database connection

    Returns:
        list of all badges
    """
    return [badge_row async for badge_row in BadgeQuerier(conn).get_badges()]


class UpdateBadgeForm(BaseModel):
    """Badge update form."""

    name: str
    description: str


@router.patch(
    "/database/badges/{badge_id}",
    status_code=status.HTTP_200_OK,
    summary="Update badge",
    description="Updates the name and description of a specific badge.",
)
async def update_badge(
    badge_id: int, form: UpdateBadgeForm, conn: database_dependency, _: AdminAuthDep
) -> Badge:
    """Update badge.

    Args:
        badge_id: badge id
        form: badge update form
        conn: database connection

    Returns:
        updated badge

    Raises:
        HTTPException: if badge not found
    """
    updated_badge = await BadgeQuerier(conn).update_badge(
        UpdateBadgeParams(
            badge_id=badge_id, name=form.name, description=form.description
        )
    )
    if not updated_badge:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Badge not found")
    return updated_badge


@router.get(
    "/database/reports/admin",
    status_code=status.HTTP_200_OK,
    summary="Get all admin issue reports",
    description="Retrieves a list of all admin issue reports in the system.",
)
async def get_admin_reports(
    conn: database_dependency, _: AdminAuthDep
) -> list[AdminIssueReport]:
    """Get all admin issue reports.

    Args:
        conn: database connection

    Returns:
        list of all admin issue reports
    """
    return [
        report_row
        async for report_row in AdminIssueReportsQuerier(conn).get_admin_issue_reports()
    ]


class UpdateReportStatusForm(BaseModel):
    """Issue report status update form."""

    status: IssueStatus


@router.patch(
    "/database/reports/admin/{report_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update admin issue report status",
    description="Updates the status of a specific admin issue report.",
)
async def update_admin_report_status(
    report_id: int,
    form: UpdateReportStatusForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> AdminIssueReport:
    """Update admin issue report status.

    Args:
        report_id: report id
        form: new status form
        conn: database connection

    Returns:
        updated report

    Raises:
        HTTPException: if report not found
    """
    updated_report = await AdminIssueReportsQuerier(
        conn
    ).update_admin_issue_report_status(
        UpdateAdminIssueReportStatusParams(report_id=report_id, status=form.status)
    )
    if not updated_report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    return updated_report


@router.get(
    "/database/reports/seller",
    status_code=status.HTTP_200_OK,
    summary="Get all seller issue reports",
    description="Retrieves a list of all seller issue reports in the system.",
)
async def get_seller_reports(
    conn: database_dependency, _: AdminAuthDep
) -> list[SellerIssueReport]:
    """Get all seller issue reports.

    Args:
        conn: database connection

    Returns:
        list of all seller issue reports
    """
    return [
        report_row
        async for report_row in SellerIssueReportsQuerier(
            conn
        ).get_seller_issue_reports()
    ]


@router.patch(
    "/database/reports/seller/{report_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update seller issue report status",
    description="Updates the status of a specific seller issue report.",
)
async def update_seller_report_status(
    report_id: int,
    form: UpdateReportStatusForm,
    conn: database_dependency,
    _: AdminAuthDep,
) -> SellerIssueReport:
    """Update seller issue report status.

    Args:
        report_id: report id
        form: new status form
        conn: database connection

    Returns:
        updated report

    Raises:
        HTTPException: if report not found
    """
    updated_report = await SellerIssueReportsQuerier(
        conn
    ).update_seller_issue_report_status(
        UpdateSellerIssueReportStatusParams(report_id=report_id, status=form.status)
    )
    if not updated_report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    return updated_report


@router.get(
    "/database/inbox",
    status_code=status.HTTP_200_OK,
    summary="Get all inbox messages",
    description="Retrieves a list of all inbox messages in the system.",
)
async def get_all_inboxes(conn: database_dependency, _: AdminAuthDep) -> list[Inbox]:
    """Get all inbox messages.

    Args:
        conn: database connection

    Returns:
        list of all inbox messages
    """
    return [inbox_row async for inbox_row in InboxQuerier(conn).get_inboxes()]


@router.get(
    "/database/inbox/user/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Get user inbox",
    description="Retrieves all inbox messages for a specific user.",
)
async def get_user_inbox(
    user_id: int, conn: database_dependency, _: AdminAuthDep
) -> list[Inbox]:
    """Get all inbox messages for a specific user.

    Args:
        user_id: user id
        conn: database connection

    Returns:
        list of all inbox messages for the user
    """
    return [
        inbox_row
        async for inbox_row in InboxQuerier(conn).get_user_inbox(user_id=user_id)
    ]


class CreateInboxMessageForm(BaseModel):
    """Inbox message creation form."""

    user_id: int
    sender_id: int
    message_subject: str
    message_text: str


@router.post(
    "/database/inbox",
    status_code=status.HTTP_201_CREATED,
    summary="Create inbox message",
    description="Creates a new inbox message in the system.",
)
async def create_inbox_message(
    form: CreateInboxMessageForm, conn: database_dependency, _: AdminAuthDep
) -> Inbox:
    """Create an inbox message.

    Args:
        form: form with the message details
        conn: database connection

    Returns:
        created inbox message

    Raises:
        HTTPException: if failed to create message
    """
    created_message = await InboxQuerier(conn).create_inbox_message(
        CreateInboxMessageParams(
            user_id=form.user_id,
            sender_id=form.sender_id,
            message_subject=form.message_subject,
            message_text=form.message_text,
        )
    )
    if not created_message:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create message"
        )
    return created_message


@router.delete(
    "/database/inbox/{message_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete inbox message",
    description="Deletes a specific inbox message from the system.",
)
async def delete_inbox_message(
    message_id: int, conn: database_dependency, _: AdminAuthDep
) -> Inbox:
    """Delete an inbox message.

    Args:
        message_id: message id
        conn: database connection

    Returns:
        deleted message

    Raises:
        HTTPException: if message not found
    """
    deleted_message = await InboxQuerier(conn).delete_inbox_message(
        message_id=message_id
    )
    if not deleted_message:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    return deleted_message
