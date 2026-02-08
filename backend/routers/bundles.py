"""Endpoints for bundles."""

from typing import Annotated
from fastapi import APIRouter, HTTPException, Security
from internal.auth.security import generate_claim_code
from internal.database.dependency import database_dependency
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.models import Bundle, Reservation
from internal.queries.token import GetSessionByTokenRow
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.reservations import CreateReservationParams, Querier as ReservationQuerier
from internal.auth.middleware import consumer_auth

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
async def reserve_bundle(bundle_id: str, conn: database_dependency, consumer: Annotated[GetSessionByTokenRow, Security(consumer_auth)]) -> Reservation:
    bundle = BundleQuerier(conn).get_bundle_lock(bundle_id=int(bundle_id))
    if not bundle:
        raise HTTPException(500, "failed to find bundle")
    reservations_querier = ReservationQuerier(conn)
    reservations = reservations_querier.get_bundle_reservations(bundle_id=int(bundle_id))
    if not reservations:
        raise HTTPException(500, "failed to find reservations")
    if bundle.total_qty <= len(list(reservations)):
        raise HTTPException(409, "no reservations available")
    reservation = reservations_querier.create_reservation(CreateReservationParams(
        bundle_id=bundle.bundle_id,
        consumer_id=consumer.user_id,
        claim_code=generate_claim_code(),
    ))
    if not reservation:
        raise HTTPException(500, "failed to create reservation")
    return reservation
