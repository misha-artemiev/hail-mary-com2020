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
    sellers.py->>creation.py: create_seller()
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

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Security
from internal.auth.creation import CreateSellerForm, create_seller
from internal.auth.middleware import seller_auth
from internal.database.dependency import database_dependency
from internal.queries.bundle import (
    CreateBundleParams,
    GetSellersBundleParams,
    UpdateBundleParams,
)
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.models import Bundle, Reservation
from internal.queries.reservations import GetReservationCollectionParams
from internal.queries.reservations import Querier as ReservationsQuerier
from internal.queries.token import GetSessionByTokenRow
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.post("", status_code=201)
async def register_seller(
    form: CreateSellerForm, conn: database_dependency
) -> Response:
    """Creates seller and coressponding user.

    Args:
      form: signup form from user
      conn: database connection

    Returns:
      if seller was registered
    """
    _ = await create_seller(form, conn)
    return Response("Seller was registered", 201)


class BundleForm(BaseModel):
    """User form for bundles."""

    bundle_name: str
    description: str
    total_qty: int
    price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: int = Field(lt=100, gt=0)
    window_start: datetime
    window_end: datetime


@router.post("/me/bundles", tags=["bundles"])
async def create_bundle(
    form: BundleForm,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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
    bundle = BundleQuerier(conn).create_bundle(
        CreateBundleParams(
            seller_id=seller.user_id,
            bundle_name=form.bundle_name,
            description=form.description,
            total_qty=form.total_qty,
            price=form.price,
            discount_percentage=form.discount_percentage,
            window_start=form.window_start,
            window_end=form.window_end,
        )
    )
    if not bundle:
        raise HTTPException(500, "failed to crete bundle")
    return bundle


@router.patch("/me/bundles/{bundle_id}", tags=["bundles"])
async def update_bundle(
    bundle_id: str,
    form: BundleForm,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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
    bundle = BundleQuerier(conn).update_bundle(
        UpdateBundleParams(
            bundle_id=int(bundle_id),
            seller_id=seller.user_id,
            bundle_name=form.bundle_name,
            description=form.description,
            total_qty=form.total_qty,
            price=form.price,
            discount_percentage=form.discount_percentage,
            window_start=form.window_start,
            window_end=form.window_end,
        )
    )
    if not bundle:
        raise HTTPException(406, "failed to update bundle")
    return bundle


@router.get("/me/bundles")
async def get_bundles(
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
) -> list[Bundle]:
    """Get sellers bundles.

    Args:
      conn: database connection
      seller: sellers connection

    Returns:
      list of sellers bundles

    Raises:
      HTTPException: if failed to get bundles
    """
    bundles = BundleQuerier(conn).get_sellers_bundles(seller_id=seller.user_id)
    if not bundles:
        raise HTTPException(500, "failed to get bundles")
    return list(bundles)


@router.get("/me/bundles/{bundle_id}/reservations", tags=["reservations"])
async def get_reservations(
    bundle_id: str,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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
    bundle = BundleQuerier(conn).get_sellers_bundle(
        GetSellersBundleParams(bundle_id=int(bundle_id), seller_id=seller.user_id)
    )
    if not bundle:
        raise HTTPException(500, "failed to find bundle")
    reservations = ReservationsQuerier(conn).get_bundle_reservations(
        bundle_id=bundle.bundle_id
    )
    if not reservations:
        raise HTTPException(500, "failed to find bundle reservations")
    return list(reservations)


@router.patch("/me/bundles/{bundle_id}/reservations/collect", tags=["reservations"])
async def reservation_collection(
    bundle_id: str,
    claim_code: str,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
) -> Reservation:
    """Confirm reservation collection.

    Args:
        bundle_id: bundle_id
        claim_code: claim code
        conn: database connection
        seller: sellers session

    Returns:
      confirmed claimed reservation

    Raises:
      HTTPException: if failed to collect reservation
    """
    reservation_querier = ReservationsQuerier(conn)
    reservation = reservation_querier.get_reservation_collection(
        GetReservationCollectionParams(bundle_id=int(bundle_id), claim_code=claim_code)
    )
    if not reservation:
        raise HTTPException(500, "failed to find reservation")
    bundle = BundleQuerier(conn).get_bundle(bundle_id=reservation.bundle_id)
    if not bundle or bundle.seller_id != seller.user_id:
        raise HTTPException(500, "failed to find bundle")
    claimed_reservation = reservation_querier.collect_reservation(
        reservation_id=reservation.reservation_id
    )
    if not claimed_reservation:
        raise HTTPException(500, "failed to update reservation status")
    return claimed_reservation
