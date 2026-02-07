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
from internal.queries.bundle import CreateBundleParams, UpdateBundleParams
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.models import Bundle
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
    _ = create_seller(form, conn)
    return Response("Seller was registered", 201)


class BundleForm(BaseModel):
    """User form for bundles."""

    bundle_name: str
    description: str
    total_qty: int
    price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: int = Field(max_digits=100, gt=0)
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


@router.put("/me/bundles/{bundle_id}", tags=["bundles"])
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
