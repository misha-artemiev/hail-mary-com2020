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

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Security,
    UploadFile,
    status,
)
from internal.auth.creation import CreateSellerForm, create_seller
from internal.auth.middleware import seller_auth
from internal.badges.engine import BadgeEngine
from internal.block.management import block_management
from internal.database.dependency import database_dependency
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.bundle import (
    CreateBundleParams,
    GetSellersBundleParams,
    UpdateBundleParams,
)
from internal.queries.models import Bundle, Reservation
from internal.queries.reservations import AsyncQuerier as ReservationsQuerier
from internal.queries.reservations import GetReservationCollectionParams
from internal.queries.seller import AsyncQuerier as SellerQuerier
from internal.queries.seller import GetSellerRow, GetSellersRow
from internal.queries.token import GetSessionByTokenRow
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
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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


class BundleForm(BaseModel):
    """User form for bundles."""

    bundle_name: str
    description: str
    total_qty: int
    price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: int = Field(lt=100, gt=0)
    weight: int
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
    bundle = await BundleQuerier(conn).create_bundle(
        CreateBundleParams(
            seller_id=seller.user_id,
            bundle_name=form.bundle_name,
            description=form.description,
            total_qty=form.total_qty,
            price=form.price,
            carbon_dioxide=form.weight,
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
    return bundle


@router.patch(
    "/me/bundles/{bundle_id}",
    tags=["bundles"],
    status_code=status.HTTP_200_OK,
    summary="Update bundle",
    description="Updates an existing bundle for the authenticated seller.",
)
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
    bundle = await BundleQuerier(conn).update_bundle(
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
            carbon_dioxide=form.weight,
        )
    )
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bundle not found or not owned by seller",
        )
    return bundle


@router.get(
    "/me/bundles",
    status_code=status.HTTP_200_OK,
    summary="Get seller bundles",
    description="Retrieves all bundles created by the authenticated seller.",
)
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
    bundle = await BundleQuerier(conn).get_sellers_bundle(
        GetSellersBundleParams(bundle_id=int(bundle_id), seller_id=seller.user_id)
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
    bundle_id: str,
    claim_code: str,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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
        GetReservationCollectionParams(bundle_id=int(bundle_id), claim_code=claim_code)
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )
    bundle = await BundleQuerier(conn).get_bundle(bundle_id=reservation.bundle_id)
    if not bundle or bundle.seller_id != seller.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found"
        )
    claimed_reservation = await reservation_querier.collect_reservation(
        reservation_id=reservation.reservation_id
    )
    if not claimed_reservation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reservation status",
        )
    await conn.commit()
    badge_engine.run(claimed_reservation.consumer_id, bundle.window_start)
    return claimed_reservation


@router.patch(
    path="/me/bundles/{bundle_id}/image", status_code=status.HTTP_202_ACCEPTED
)
async def change_bundle_image(
    bundle_id: int,
    file: UploadFile,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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


@router.get(path="/me/bundles/{bundle_id}/image", status_code=status.HTTP_200_OK)
async def get_bundle_image(
    bundle_id: int,
    conn: database_dependency,
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
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
