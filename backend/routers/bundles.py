"""Endpoints for bundles."""

from datetime import datetime
from math import ceil

from fastapi import APIRouter, HTTPException, Response, status
from internal.auth.middleware import ConsumerAuthDep
from internal.auth.security import generate_claim_code
from internal.block.management import block_management
from internal.database.dependency import database_dependency
from internal.geolocation.distance import dist_safe_box, get_distance
from internal.geolocation.types import LocationModel
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.inbox import AsyncQuerier as InboxQuerier
from internal.queries.inbox import CreateInboxMessageParams
from internal.queries.models import Bundle, Reservation
from internal.queries.reservations import AsyncQuerier as ReservationQuerier
from internal.queries.reservations import CreateReservationParams
from internal.queries.seller import AsyncQuerier as SellerQuerier
from internal.queries.seller import GetSellerByLocationParams
from internal.search.bundle_search import filter_bundle
from internal.settings.env import host_settings
from pydantic import BaseModel, Field
from thefuzz.fuzz import WRatio  # type: ignore[import-untyped]

router = APIRouter(prefix="/bundles", tags=["bundles"])

BUNDLES_PER_PAGE = 30


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Get all bundles",
    description="Retrieves a list of all available bundles.",
)
async def get_bundles(conn: database_dependency) -> list[Bundle]:
    """Get all bundles.

    Args:
      conn: database connection

    Returns:
      all bundles in an iterator

    Raises:
      HTTPException: if failed to get bundles
    """
    bundles = [item async for item in BundleQuerier(conn).get_bundles()]
    if bundles is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find bundles",
        )
    return list(bundles)


@router.get(
    "/{bundle_id}",
    status_code=status.HTTP_200_OK,
    summary="Get bundle by ID",
    description="Retrieves details of a specific bundle by its ID.",
)
async def get_bundle(bundle_id: str, conn: database_dependency) -> Bundle:
    """Get bundle.

    Args:
      bundle_id: bundle id
      conn: database connection

    Returns:
      found bundle

    Raises:
      HTTPException: if failed to find a bundle
    """
    bundle = await BundleQuerier(conn).get_bundle(bundle_id=int(bundle_id))
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found"
        )
    return bundle


@router.post(
    "/{bundle_id}/reservations",
    tags=["reservations"],
    status_code=status.HTTP_201_CREATED,
    summary="Reserve a bundle",
    description=(
        "Creates a reservation for a specific bundle for the authenticated consumer."
    ),
)
async def reserve_bundle(
    bundle_id: str, conn: database_dependency, consumer: ConsumerAuthDep
) -> Reservation:
    """Create bundle reservation.

    Args:
        bundle_id: bundle id
        conn: database connection
        consumer: consumer session

    Returns:
        found reservation

    Raises:
        HTTPException: if failed to create reservation
    """
    bundle = await BundleQuerier(conn).get_bundle_lock(bundle_id=int(bundle_id))
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found"
        )
    reservations_querier = ReservationQuerier(conn)
    reservations = [
        item
        async for item in reservations_querier.get_bundle_reservations(
            bundle_id=int(bundle_id)
        )
    ]
    if reservations is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find reservations",
        )
    if bundle.total_qty <= len(list(reservations)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="No reservations available"
        )
    used_codes = [rese.claim_code for rese in reservations]
    reservation = await reservations_querier.create_reservation(
        CreateReservationParams(
            bundle_id=bundle.bundle_id,
            consumer_id=consumer.user_id,
            claim_code=generate_claim_code(used_codes),
        )
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reservation",
        )

    await InboxQuerier(conn).create_inbox_message(
        CreateInboxMessageParams(
            user_id=consumer.user_id,
            sender_id=consumer.user_id,
            message_subject="Bundle reserved",
            message_text=(
                f"You reserved '{bundle.bundle_name}'. "
                f"Your claim code is {reservation.claim_code}. "
                "This reservation expires when the pickup window ends at "
                f"{bundle.window_end.strftime('%Y-%m-%d %H:%M UTC')}."
            ),
        )
    )
    await InboxQuerier(conn).create_inbox_message(
        CreateInboxMessageParams(
            user_id=bundle.seller_id,
            sender_id=consumer.user_id,
            message_subject="Bundle reserved",
            message_text=(
                "A reservation has been created for your bundle "
                f"'{bundle.bundle_name}'."
            ),
        )
    )

    return reservation


class SearchBundlesForm(BaseModel):
    """Consumer search form with parameters."""

    lat: float
    lon: float
    max_dist: int = Field(gt=0)
    max_price: float | None = Field(gt=0)
    seller_name: str | None
    allergens: list[int] | None
    categories: list[int] | None
    page: int = Field(gt=0, default=1)


class SearchBundlesResponse(BaseModel):
    """Search response item with card information."""

    bundle_id: int
    sellers_name: str
    bundle_name: str
    bundle_description: str
    price: float
    discount_percentage: int
    window_start: datetime
    window_end: datetime
    dist: float
    search_score: float | None = None


@router.post(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search bundles",
    description=(
        "Searches for bundles based on location, distance, price, and other filters."
    ),
)
async def search_bundles(
    form: SearchBundlesForm, conn: database_dependency
) -> tuple[int, list[SearchBundlesResponse]]:
    """Bundle search with parameters endpoint.

    Args:
      form: consumer search parameters
      conn: database connection

    Returns:
      found bundles card information
    """
    distance_box = dist_safe_box(
        LocationModel(lat=form.lat, lon=form.lon), form.max_dist
    )
    sellers = [
        item
        async for item in SellerQuerier(conn).get_seller_by_location(
            GetSellerByLocationParams(
                lat_max=distance_box.lat_max,
                lat_min=distance_box.lat_min,
                lon_max=distance_box.lon_max,
                lon_min=distance_box.lon_min,
            )
        )
    ]
    filtered_bundles: list[SearchBundlesResponse] = []
    for seller in sellers:
        dist = get_distance(
            LocationModel(lat=form.lat, lon=form.lon),
            LocationModel(lat=seller.latitude, lon=seller.longitude),
        )
        if dist > form.max_dist:
            continue
        if (
            form.seller_name
            and WRatio(form.seller_name, seller.seller_name)
            < host_settings.fuzz_threshold
        ):
            continue
        seller_bundles = [
            item
            async for item in BundleQuerier(conn).get_sellers_active_bundles(
                seller_id=seller.user_id
            )
        ]
        for bundle in seller_bundles:
            if not await filter_bundle(
                conn, bundle, form.allergens, form.categories, form.max_price
            ):
                continue
            filtered_bundles.append(
                SearchBundlesResponse(
                    bundle_id=bundle.bundle_id,
                    sellers_name=seller.seller_name,
                    bundle_name=bundle.bundle_name,
                    bundle_description=bundle.description,
                    price=float(bundle.price),
                    discount_percentage=bundle.discount_percentage,
                    window_start=bundle.window_start,
                    window_end=bundle.window_end,
                    dist=round(dist, 2),
                )
            )

    if form.seller_name:
        for fb in filtered_bundles:
            fb.search_score = WRatio(form.seller_name, fb.sellers_name)
        filtered_bundles = [
            fb
            for fb in filtered_bundles
            if fb.search_score and fb.search_score >= host_settings.fuzz_threshold
        ]
        filtered_bundles.sort(
            key=lambda x: (-(x.search_score or 0), x.dist, -x.discount_percentage)
        )
    else:
        filtered_bundles.sort(key=lambda x: (x.dist, -x.discount_percentage))

    pages = ceil(len(filtered_bundles) / BUNDLES_PER_PAGE)
    start_idx = (form.page - 1) * BUNDLES_PER_PAGE
    end_idx = start_idx + BUNDLES_PER_PAGE
    page_bundles = filtered_bundles[start_idx:end_idx]
    return (pages, page_bundles)


@router.get(
    path="/{bundle_id}/image",
    status_code=status.HTTP_200_OK,
    summary="Get bundle image",
    description="Retrieves the image for a specific bundle.",
)
async def get_bundle_image(bundle_id: int, conn: database_dependency) -> Response:
    """Get bundle image.

    Args:
        bundle_id: bundle id
        conn: database connection

    Returns:
        bundle image

    Raises:
        HTTPException: if failed to get image
    """
    if BundleQuerier(conn).get_bundle(bundle_id=bundle_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "bundle not found")
    return Response(
        block_management.get_bundle_image(bundle_id), media_type="image/jpeg"
    )
