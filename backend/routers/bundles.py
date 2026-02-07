"""Endpoints for bundles."""

from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from internal.database.dependency import database_dependency
from internal.queries.bundle import Querier as BundleQuerier
from internal.queries.models import Bundle

router = APIRouter(prefix="/bundles", tags=["bundles"])


@router.get("/", tags=["bundles"])
async def get_bundles(conn: database_dependency) -> Iterator[Bundle]:
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
    return bundles


@router.get("/{bundle_id}", tags=["bundles"])
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
