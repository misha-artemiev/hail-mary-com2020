"""Endpoints for sellers.

```mermaid
---
config:
  mirrorActors: false
---
sequenceDiagram
    title Seller Registration
    actor user
    box ./routers
    participant sellers.py@{ "type" : "boundary" }
    end
    box ./internal/database
    participant dd as database.py
    end
    box ./internal/auth
    participant creation.py
    participant security.py
    end
    box ./internal/queries
    participant user.py
    participant sq as seller.py
    end
    participant database@{ "type" : "database" }

    user->>sellers.py: register seller
    activate sellers.py
    dd->>sellers.py: yield connection
    activate dd
    sellers.py->>creation.py: await create_seller()
    activate creation.py
    creation.py->>creation.py: create_user()
    creation.py->>security.py: hash_password()
    activate security.py
    security.py-->>creation.py: password hash
    deactivate security.py
    creation.py->>user.py: Queries.create_user()
    activate user.py
    user.py->>database: insert user
    activate database
    database-->>user.py: created user
    deactivate database
    user.py-->>creation.py: created user
    deactivate user.py
    creation.py-->>creation.py: created user
    creation.py->>sq: Queries.create_seller()
    activate sq
    sq->>database: insert seller
    activate database
    database-->>sq: created seller
    deactivate database
    sq-->>creation.py: created seller
    deactivate sq
    creation.py-->>sellers.py: created seller
    deactivate creation.py
    sellers.py-->>user: 201 OK
    sellers.py-->>dd: return connection
    deactivate dd
    deactivate sellers.py
```
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from internal.analytics.co2_estimator import estimate_carbon_doixide_saved
from internal.analytics.processing import AnalyticsProcesser
from internal.auth.creation import CreateSellerForm, create_seller
from internal.auth.middleware import SellerAuthDep
from internal.badges.engine import BadgeEngine
from internal.block.management import block_management
from internal.database.dependency import database_dependency
from internal.inbox.notifications import send_notification
from internal.queries.allergens import (
    AddBundlesAllergenParams,
    DeleteBundleAllergenParams,
)
from internal.queries.allergens import AsyncQuerier as AllergenQuerier
from internal.queries.analytics import AsyncQuerier as AnalyticsQuerier
from internal.queries.analytics import GetGraphParams
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.bundle import (
    CreateBundleParams,
    GetSellersBundleParams,
    UpdateBundleParams,
)
from internal.queries.category import (
    AddBundlesCategoryParams,
    DeleteBundleCategoryParams,
)
from internal.queries.category import AsyncQuerier as CategoryQuerier
from internal.queries.models import (
    AnalyticsGraph,
    AnalyticsGraphsType,
    AnalyticsPoint,
    AnalyticsSeries,
    Bundle,
    Reservation,
)
from internal.queries.reservations import AsyncQuerier as ReservationsQuerier
from internal.queries.reservations import GetReservationCollectionParams
from internal.queries.seller import AsyncQuerier as SellerQuerier
from internal.queries.seller import GetSellerRow, GetSellersRow, UpdateSellerParams
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get all sellers",
    description="Retrieves a list of all registered sellers.",
)
async def get_sellers(conn: database_dependency) -> list[GetSellersRow]:
    """Get all sellers.

    Args:
      conn: database connection

    Returns:
      list of all sellers
    """
    return [seller async for seller in SellerQuerier(conn).get_sellers()]


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get authenticated seller",
    description="Retrieves the profile of the authenticated seller.",
)
async def get_seller_me(
    conn: database_dependency, seller: SellerAuthDep
) -> GetSellerRow:
    """Get authenticated seller profile.

    Args:
      conn: database connection
      seller: sellers session

    Returns:
      seller profile

    Raises:
      HTTPException: if seller not found
    """
    seller_profile = await SellerQuerier(conn).get_seller(user_id=seller.user_id)
    if not seller_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found"
        )
    return seller_profile


@router.get(
    "/{seller_id}",
    status_code=status.HTTP_200_OK,
    summary="Get seller by ID",
    description="Retrieves the profile of a seller by their unique ID.",
)
async def get_seller_by_id(seller_id: int, conn: database_dependency) -> GetSellerRow:
    """Get seller profile by ID.

    Args:
      seller_id: unique identifier of the seller
      conn: database connection

    Returns:
      seller profile

    Raises:
      HTTPException: if seller not found
    """
    seller_profile = await SellerQuerier(conn).get_seller(user_id=seller_id)
    if not seller_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found"
        )
    return seller_profile


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Register seller",
    description="Creates a new seller and their corresponding user entity.",
)
async def register_seller(form: CreateSellerForm, conn: database_dependency) -> None:
    """Creates seller and coressponding user.

    Args:
      form: signup form from user
      conn: database connection
    """
    _ = await create_seller(form, conn)


class UpdateSellerForm(BaseModel):
    """Form for updating seller profile."""

    address_line1: str
    address_line2: str | None = None
    city: str
    post_code: str
    region: str | None = None
    country: str
    latitude: float | None = None
    longitude: float | None = None


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Update seller profile",
    description="Updates the profile information for the authenticated seller.",
)
async def update_seller(
    form: UpdateSellerForm, conn: database_dependency, seller: SellerAuthDep
) -> None:
    """Update seller profile.

    Args:
        form: seller update form
        conn: database connection
        seller: seller session

    Raises:
        HTTPException: if failed to update seller
    """
    seller_querier = SellerQuerier(conn)
    seller_record = await seller_querier.get_seller(user_id=seller.user_id)
    if seller_record is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to get seller"
        )
    updated_seller = await seller_querier.update_seller(
        UpdateSellerParams(
            user_id=seller.user_id,
            seller_name=seller_record.seller_name,
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
    if not updated_seller:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update seller",
        )


class BundleForm(BaseModel):
    """User form for bundles."""

    bundle_name: str
    description: str
    total_qty: int
    price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: int = Field(lt=100, gt=0)
    weight: int
    categories: list[int] = Field(min_length=1)
    allergens: list[int]
    window_start: datetime
    window_end: datetime


@router.post(
    "/me/bundles",
    tags=["bundles"],
    status_code=status.HTTP_201_CREATED,
    summary="Create bundle",
    description="Creates a new bundle for the authenticated seller.",
)
async def create_bundle(
    form: BundleForm, conn: database_dependency, seller: SellerAuthDep
) -> Bundle:
    """Create bundle.

    Args:
      form: bundle info form
      conn: database connection
      seller: sellers session

    Returns:
      created bundle

    Raises:
      HTTPException: if failed to create bundle
    """
    category_querier = CategoryQuerier(conn)
    allergen_querier = AllergenQuerier(conn)
    coefficients: list[float] = []
    for category in form.categories:
        if (
            category_record := await category_querier.get_category(category_id=category)
        ) is None:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to get category coefficient",
            )
        coefficients.append(category_record.category_coefficient)
    carbon_dioxide = estimate_carbon_doixide_saved(coefficients, weight_g=form.weight)
    bundle = await BundleQuerier(conn).create_bundle(
        CreateBundleParams(
            seller_id=seller.user_id,
            bundle_name=form.bundle_name,
            description=form.description,
            total_qty=form.total_qty,
            price=form.price,
            carbon_dioxide=carbon_dioxide,
            discount_percentage=form.discount_percentage,
            window_start=form.window_start,
            window_end=form.window_end,
        )
    )
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bundle",
        )
    for category in form.categories:
        bundle_category = await category_querier.add_bundles_category(
            AddBundlesCategoryParams(bundle_id=bundle.bundle_id, category_id=category)
        )
        if bundle_category is None:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to add bundle category"
            )
    for allergen in form.allergens:
        bundle_allergen = await allergen_querier.add_bundles_allergen(
            AddBundlesAllergenParams(bundle_id=bundle.bundle_id, allergen_id=allergen)
        )
        if bundle_allergen is None:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to add bundle allergen"
            )

    await send_notification(
        conn,
        user_id=seller.user_id,
        sender_id=seller.user_id,
        subject="Bundle listed",
        text=(
            f"Your bundle '{bundle.bundle_name}' is now listed "
            f"and available for reservations."
        ),
    )
    return bundle


async def update_bundle_categories(
    bundle_id: int, category_querier: CategoryQuerier, form: BundleForm
) -> None:
    """Update bundle categories to a new once.

    Args:
        bundle_id: bundle id
        category_querier: categories async querier
        form: update bundle form

    Raises:
        HTTPException: if failed to update categories
    """
    bundle_categories = [
        bundle_category
        async for bundle_category in category_querier.get_bundle_categories(
            bundle_id=bundle_id
        )
    ]
    for category in form.categories:
        if category not in bundle_categories:
            added_category = await category_querier.add_bundles_category(
                AddBundlesCategoryParams(bundle_id=bundle_id, category_id=category)
            )
            if added_category is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Failed to add bundle category",
                )
    for bundle_category in bundle_categories:
        if bundle_category not in form.categories:
            deleted_category = await category_querier.delete_bundle_category(
                DeleteBundleCategoryParams(
                    bundle_id=bundle_id, category_id=bundle_category
                )
            )
            if deleted_category is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "failed to delete bundle category",
                )


async def update_bundle_allergens(
    bundle_id: int, allergen_querier: AllergenQuerier, form: BundleForm
) -> None:
    """Update bandle allergens to a new once.

    Args:
        bundle_id: bundle id
        allergen_querier: allergen async querier
        form: bundle update form

    Raises:
        HTTPException: if failed to update allergens
    """
    bundle_allergens = [
        bundle_allergen
        async for bundle_allergen in allergen_querier.get_bundle_allergens(
            bundle_id=bundle_id
        )
    ]
    for allergen in form.allergens:
        if allergen not in bundle_allergens:
            added_allergen = await allergen_querier.add_bundles_allergen(
                AddBundlesAllergenParams(bundle_id=bundle_id, allergen_id=allergen)
            )
            if added_allergen is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Failed to add bundle allergen",
                )
    for bundle_allergen in bundle_allergens:
        if bundle_allergen not in form.allergens:
            deleted_allergen = await allergen_querier.delete_bundle_allergen(
                DeleteBundleAllergenParams(
                    bundle_id=bundle_id, allergen_id=bundle_allergen
                )
            )
            if deleted_allergen is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "failed to delete bundle allergen",
                )


@router.patch(
    "/me/bundles/{bundle_id}",
    tags=["bundles"],
    status_code=status.HTTP_200_OK,
    summary="Update bundle",
    description="Updates an existing bundle for the authenticated seller.",
)
async def update_bundle(
    bundle_id: int, form: BundleForm, conn: database_dependency, seller: SellerAuthDep
) -> Bundle:
    """Update bundle.

    Args:
      bundle_id: bundle id
      form: updated bundle info form
      conn: database connection
      seller: sellers session

    Returns:
      updated bundle

    Raises:
      HTTPException: if failed to update bundle
    """
    category_querier = CategoryQuerier(conn)
    allergen_querier = AllergenQuerier(conn)
    coefficients: list[float] = []
    for category in form.categories:
        if (
            category_record := await category_querier.get_category(category_id=category)
        ) is None:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to get category coefficient",
            )
        coefficients.append(category_record.category_coefficient)
    carbon_dioxide = estimate_carbon_doixide_saved(coefficients, weight_g=form.weight)
    bundle = await BundleQuerier(conn).update_bundle(
        UpdateBundleParams(
            bundle_id=bundle_id,
            seller_id=seller.user_id,
            bundle_name=form.bundle_name,
            description=form.description,
            total_qty=form.total_qty,
            price=form.price,
            discount_percentage=form.discount_percentage,
            window_start=form.window_start,
            window_end=form.window_end,
            carbon_dioxide=carbon_dioxide,
        )
    )
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bundle not found or not owned by seller",
        )
    await update_bundle_categories(bundle_id, category_querier, form)
    await update_bundle_allergens(bundle_id, allergen_querier, form)
    return bundle


@router.get(
    "/me/bundles",
    status_code=status.HTTP_200_OK,
    summary="Get seller bundles",
    description="Retrieves all bundles created by the authenticated seller.",
)
async def get_bundles(conn: database_dependency, seller: SellerAuthDep) -> list[Bundle]:
    """Get sellers bundles.

    Args:
      conn: database connection
      seller: sellers connection

    Returns:
      list of sellers bundles

    Raises:
      HTTPException: if failed to get bundles
    """
    bundles = [
        item
        async for item in BundleQuerier(conn).get_sellers_bundles(
            seller_id=seller.user_id
        )
    ]
    if bundles is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get bundles",
        )

    now = datetime.now(tz=UTC)
    for bundle in bundles:
        if bundle.window_end <= now:
            await send_notification(
                conn,
                user_id=seller.user_id,
                sender_id=seller.user_id,
                subject="Bundle expired",
                text=(
                    f"Your bundle '{bundle.bundle_name}' has expired at "
                    f"{bundle.window_end.strftime('%Y-%m-%d %H:%M UTC')}."
                ),
            )

    return list(bundles)


@router.get(
    "/me/bundles/{bundle_id}/reservations",
    tags=["reservations"],
    status_code=status.HTTP_200_OK,
    summary="Get bundle reservations",
    description=(
        "Retrieves all reservations for a specific bundle owned "
        "by the authenticated seller."
    ),
)
async def get_reservations(
    bundle_id: int, conn: database_dependency, seller: SellerAuthDep
) -> list[Reservation]:
    """Get reservations for sellers bundle.

    Args:
      bundle_id: bundle id
      conn: database connection
      seller: sellers session

    Returns:
        list of reservations for specific bundle

    Raises:
        HTTPException: if failed to get reservations
    """
    bundle = await BundleQuerier(conn).get_sellers_bundle(
        GetSellersBundleParams(bundle_id=bundle_id, seller_id=seller.user_id)
    )
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found"
        )
    reservations = [
        item
        async for item in ReservationsQuerier(conn).get_bundle_reservations(
            bundle_id=bundle.bundle_id
        )
    ]
    if reservations is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find bundle reservations",
        )
    return list(reservations)


@router.patch(
    "/me/bundles/{bundle_id}/reservations/collect",
    tags=["reservations"],
    status_code=status.HTTP_200_OK,
    summary="Collect reservation",
    description="Confirms the collection of a reservation using a claim code.",
)
async def reservation_collection(
    bundle_id: int,
    claim_code: str,
    conn: database_dependency,
    seller: SellerAuthDep,
    badge_engine: Annotated[BadgeEngine, Depends(BadgeEngine)],
) -> Reservation:
    """Confirm reservation collection.

    Args:
        bundle_id: bundle_id
        claim_code: claim code
        conn: database connection
        seller: sellers session
        badge_engine: badge acquiry engine

    Returns:
      confirmed claimed reservation

    Raises:
      HTTPException: if failed to collect reservation
    """
    reservation_querier = ReservationsQuerier(conn)
    reservation = await reservation_querier.get_reservation_collection(
        GetReservationCollectionParams(bundle_id=bundle_id, claim_code=claim_code)
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )
    bundle = await BundleQuerier(conn).get_bundle(bundle_id=reservation.bundle_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found"
        )
    if bundle.seller_id != seller.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reservation does not belong to your bundle",
        )
    claimed_reservation = await reservation_querier.collect_reservation(
        reservation_id=reservation.reservation_id
    )
    if not claimed_reservation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reservation status",
        )

    await send_notification(
        conn,
        user_id=seller.user_id,
        sender_id=seller.user_id,
        subject="Bundle collected",
        text=(
            f"A reservation for bundle '{bundle.bundle_name}' has been collected successfully."
        ),
    )
    await send_notification(
        conn,
        user_id=claimed_reservation.consumer_id,
        sender_id=seller.user_id,
        subject="Reservation collected",
        text=(
            f"Your reservation for '{bundle.bundle_name}' has been marked as collected."
        ),
    )

    await conn.commit()
    badge_engine.run(claimed_reservation.consumer_id, bundle.window_start)
    return claimed_reservation


@router.post(
    "/me/analytics",
    tags=["analytics"],
    summary="Refresh analytics",
    description="Triggers a refresh of analytics graphs for the authenticated seller.",
)
async def refresh_analytics(
    seller: SellerAuthDep,
    analytics_processer: Annotated[AnalyticsProcesser, Depends(AnalyticsProcesser)],
) -> None:
    """Refresh analytics graphs for the authenticated seller.

    Args:
        seller: authenticated seller session
        analytics_processer: analytics processing engine
    """
    analytics_processer.run(seller.user_id)


@router.patch(
    path="/me/bundles/{bundle_id}/image",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Change bundle image",
    description="Updates the image for a bundle owned by the authenticated seller.",
)
async def change_bundle_image(
    bundle_id: int, file: UploadFile, conn: database_dependency, seller: SellerAuthDep
) -> None:
    """Change bundle image.

    Args:
        bundle_id: bundle id
        file: bundle image
        conn: database connection
        seller: seller session

    Raises:
        HTTPException: if failed to change image
    """
    if (
        BundleQuerier(conn).get_sellers_bundle(
            GetSellersBundleParams(seller_id=seller.user_id, bundle_id=bundle_id)
        )
        is None
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "bundle not found")
    await block_management.upload_bundle_image(bundle_id, file)


@router.get(
    path="/me/bundles/{bundle_id}/image",
    status_code=status.HTTP_200_OK,
    summary="Get bundle image",
    description="Retrieves the image for a bundle owned by the authenticated seller.",
)
async def get_bundle_image(
    bundle_id: int, conn: database_dependency, seller: SellerAuthDep
) -> Response:
    """Get bundle image.

    Args:
        bundle_id: bundle id
        conn: database connection
        seller: seller session

    Returns:
        bundle image

    Raises:
        HTTPException: if failed to get bundle image
    """
    if (
        BundleQuerier(conn).get_sellers_bundle(
            GetSellersBundleParams(seller_id=seller.user_id, bundle_id=bundle_id)
        )
        is None
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "bundle not found")
    return Response(
        block_management.get_bundle_image(bundle_id), media_type="image/jpeg"
    )


@router.get(
    "/me/analytics",
    status_code=status.HTTP_200_OK,
    tags=["analytics"],
    summary="Get analytics graph types",
    description="Retrieves all available analytics graph types for the seller.",
)
async def get_analytics_graph_types(
    conn: database_dependency, _: SellerAuthDep
) -> list[AnalyticsGraphsType]:
    """Get all graph types.

    Args:
        conn: database connection

    Returns:
        list of all graph types
    """
    return [
        graph_type async for graph_type in AnalyticsQuerier(conn).get_graphs_types()
    ]


@router.get(
    "/me/analytics/{graph_type_id}",
    status_code=status.HTTP_200_OK,
    tags=["analytics"],
    summary="Get analytics graph",
    description="Retrieves an analytics graph with series and points for the seller.",
)
async def get_analytics_graph(
    graph_type_id: int, conn: database_dependency, seller: SellerAuthDep
) -> tuple[AnalyticsGraph, list[tuple[AnalyticsSeries, list[AnalyticsPoint]]]]:
    """Get analytics graph.

    Args:
        graph_type_id: graph type id
        conn: database connection
        seller: seller session

    Returns:
        graph, series and points

    Raises:
        HTTPException: if failed to get graph
    """
    analytics_querier = AnalyticsQuerier(conn)
    if (await analytics_querier.get_graph_type(graph_type_id=graph_type_id)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "failed to find graph type")
    if (
        graph := await analytics_querier.get_graph(
            GetGraphParams(seller_id=seller.user_id, graph_type=graph_type_id)
        )
    ) is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to get graph"
        )
    series = [
        series
        async for series in analytics_querier.get_graph_series(graph_id=graph.graph_id)
    ]
    if len(series) == 0:
        return (graph, [])
    series_and_points: list[tuple[AnalyticsSeries, list[AnalyticsPoint]]] = []
    for single_series in series:
        single_series_points: list[AnalyticsPoint] = [
            point
            async for point in analytics_querier.get_graph_points(
                series_id=single_series.series_id
            )
        ]
        series_and_points.append((single_series, single_series_points))
    return (graph, series_and_points)
