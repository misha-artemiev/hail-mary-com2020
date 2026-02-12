"""Endpoints for bundles."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Security
from internal.auth.middleware import consumer_auth
from internal.auth.security import generate_claim_code
from internal.database.dependency import database_dependency
from internal.geolocation.distance import dist_safe_box, get_distance
from internal.geolocation.types import LocationModel
from internal.queries.allergens import Querier as AllergensQuerier
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.category import Querier as CategoriesQuerier
from internal.queries.models import Bundle, Reservation
from internal.queries.reservations import CreateReservationParams
from internal.queries.reservations import Querier as ReservationQuerier
from internal.queries.seller import GetSellerByLocationParams
from internal.queries.seller import Querier as SellerQuerier
from internal.queries.token import GetSessionByTokenRow
from internal.settings.env import host_settings
from pydantic import BaseModel, Field
from thefuzz.fuzz import WRatio  # type: ignore[import-untyped]
from internal.logger.logger import logger

router = APIRouter(prefix="/bundles", tags=["bundles"])


@router.get("/")
async def get_bundles(conn: database_dependency) -> list[Bundle]:
    """Get all bundles.

    Args:
      conn: database connection

    Returns:
      all bundles in an iterator

    Raises:
      HTTPException: if failed to get bundles
    """
    bundles = BundleQuerier(conn).get_bundles()
    if not bundles:
        raise HTTPException(500, "failed to find bundles")
    return list(bundles)


@router.get("/{bundle_id}")
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
    bundle = BundleQuerier(conn).get_bundle(bundle_id=int(bundle_id))
    if not bundle:
        raise HTTPException(500, "failed to find bundle")
    return bundle


@router.post("/{bundle_id}/reservations", tags=["reservations"])
async def reserve_bundle(
    bundle_id: str,
    conn: database_dependency,
    consumer: Annotated[GetSessionByTokenRow, Security(consumer_auth)],
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
    bundle = BundleQuerier(conn).get_bundle_lock(bundle_id=int(bundle_id))
    if not bundle:
        raise HTTPException(500, "failed to find bundle")
    reservations_querier = ReservationQuerier(conn)
    reservations = reservations_querier.get_bundle_reservations(
        bundle_id=int(bundle_id)
    )
    if not reservations:
        raise HTTPException(500, "failed to find reservations")
    if bundle.total_qty <= len(list(reservations)):
        raise HTTPException(409, "no reservations available")
    used_codes = [rese.claim_code for rese in reservations]
    reservation = reservations_querier.create_reservation(
        CreateReservationParams(
            bundle_id=bundle.bundle_id,
            consumer_id=consumer.user_id,
            claim_code=generate_claim_code(used_codes),
        )
    )
    if not reservation:
        raise HTTPException(500, "failed to create reservation")
    return reservation


class SearchBundlesForm(BaseModel):
    """Consumer search form with parameters."""

    lat: float
    lon: float
    max_dist: int | None = Field(gt=0)
    max_price: float | None = Field(gt=0)
    seller_name: str | None
    allergens: list[int] | None
    categories: list[int] | None


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


@router.post("/search")
async def search_bundles(
    form: SearchBundlesForm, conn: database_dependency
) -> list[SearchBundlesResponse]:
    """Bundle search with parameters endpoint.

    Args:
      form: consumer search parameters
      conn: database connection

    Returns:
      found bundles card information

    Raises:
        HTTPException: if failed to find item
    """
    form.max_dist = form.max_dist or 10
    distance_box = dist_safe_box(
        LocationModel(lat=form.lat, lon=form.lon), form.max_dist
    )
    sellers = SellerQuerier(conn).get_seller_by_location(
        GetSellerByLocationParams(
            lat_max=distance_box.lat_max,
            lat_min=distance_box.lat_min,
            lon_max=distance_box.lon_max,
            lon_min=distance_box.lon_min,
        )
    )
    if not sellers:
        raise HTTPException(500, "failed to get sellers")
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
        seller_bundles = BundleQuerier(conn).get_sellers_active_bundles(
            seller_id=seller.user_id
        )
        for bundle in seller_bundles:
            allergens = AllergensQuerier(conn).get_bundle_allergens(
                bundle_id=bundle.bundle_id
            )
            if (
                allergens
                and form.allergens
                and not set(list(allergens)).isdisjoint(set(form.allergens))
            ):
                continue
            categories = CategoriesQuerier(conn).get_bundle_categories(
                bundle_id=bundle.bundle_id
            )
            if (
                categories
                and form.categories
                and set(list(categories)).isdisjoint(set(form.categories))
            ):
                continue
            reservations = ReservationQuerier(conn).get_bundle_reservations(
                bundle_id=int(bundle.bundle_id)
            )
            if not reservations or bundle.total_qty <= len(list(reservations)):
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
    return filtered_bundles
