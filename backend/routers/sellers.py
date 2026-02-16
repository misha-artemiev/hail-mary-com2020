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

import base64
import importlib.util
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import ModuleType
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

GRAPH_FILE_NAMES = {
    "top_time_windows": "top_time_windows.png",
    "sell_rate_capacity": "sell_rate_capacity.png",
    "top_categories": "top_categories.png",
}
GRAPH_TITLES = {
    "top_time_windows": "Top Collection Time Windows",
    "sell_rate_capacity": "Sell Rate vs Capacity",
    "top_categories": "Top Categories by Reservations",
}


def _load_sourceless_module(module_name: str, module_path: Path) -> ModuleType:
    """Load a module from `.pyc` when source files are unavailable."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise ImportError(f"failed to build import spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _try_generate_graph_paths(seller_id: int) -> dict[str, Path]:
    """Try generating graph files with analytics modules."""
    try:
        from database.data.graphs import generate_seller_weekly_graphs

        generated_paths = generate_seller_weekly_graphs(seller_user_id=seller_id)
        if isinstance(generated_paths, dict):
            resolved: dict[str, Path] = {}
            for key, raw_path in generated_paths.items():
                if key not in GRAPH_FILE_NAMES:
                    continue
                path = Path(str(raw_path))
                if path.exists():
                    resolved[key] = path.resolve()
            if resolved:
                return resolved
    except Exception:
        pass

    # Fallback to compiled modules if source imports are unavailable.
    backend_root = Path(__file__).resolve().parents[1]
    cache_dir = backend_root / "database" / "data" / "__pycache__"
    data_analysis_pyc = next(
        cache_dir.glob("DataAnalysis.cpython-*.pyc"),
        None,
    )
    graphs_pyc = next(cache_dir.glob("graphs.cpython-*.pyc"), None)
    if not data_analysis_pyc or not graphs_pyc:
        return {}

    try:
        _load_sourceless_module("database.data.DataAnalysis", data_analysis_pyc)
        graphs_module = _load_sourceless_module(
            "database.data._graphs_runtime",
            graphs_pyc,
        )
        generate = getattr(graphs_module, "generate_seller_weekly_graphs", None)
        if not callable(generate):
            return {}
        generated_paths = generate(seller_id)
    except Exception:
        return {}

    if not isinstance(generated_paths, dict):
        return {}

    resolved: dict[str, Path] = {}
    for key, raw_path in generated_paths.items():
        if key not in GRAPH_FILE_NAMES:
            continue
        path = Path(str(raw_path))
        if not path.is_absolute():
            path = (backend_root / path).resolve()
        if path.exists():
            resolved[key] = path
    return resolved


def _find_latest_graph_paths(seller_id: int) -> tuple[str | None, dict[str, Path]]:
    """Find latest pre-generated analytics graph files for a seller."""
    graphs_root = (
        Path(__file__).resolve().parents[1]
        / "database"
        / "data"
        / "graphs"
        / f"seller_{seller_id}"
    )
    if not graphs_root.exists():
        return None, {}

    report_dirs = sorted((path for path in graphs_root.iterdir() if path.is_dir()))
    if not report_dirs:
        return None, {}

    latest_dir = report_dirs[-1]
    paths: dict[str, Path] = {}
    for key, filename in GRAPH_FILE_NAMES.items():
        graph_path = latest_dir / filename
        if graph_path.exists():
            paths[key] = graph_path
    return latest_dir.name, paths


def _get_graph_paths_for_seller(seller_id: int) -> tuple[str | None, dict[str, Path]]:
    """Resolve graph paths for a seller from generated output or existing files."""
    graph_paths = _try_generate_graph_paths(seller_id)
    if graph_paths:
        report_period = next(iter(graph_paths.values())).parent.name
        return report_period, graph_paths
    return _find_latest_graph_paths(seller_id)


class AnalyticsGraph(BaseModel):
    """Seller analytics graph payload."""

    key: str
    title: str
    image_data_url: str


class AnalyticsGraphsResponse(BaseModel):
    """Seller analytics page payload."""

    seller_user_id: int
    report_period: str | None
    graphs: list[AnalyticsGraph]


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


@router.get("/me/analytics/graphs", tags=["analytics"])
async def get_seller_analytics_graphs(
    seller: Annotated[GetSessionByTokenRow, Security(seller_auth)],
) -> AnalyticsGraphsResponse:
    """Fetch seller analytics graphs for the authenticated seller."""
    report_period = None
    graph_paths: dict[str, Path] = {}
    selected_seller_id = seller.user_id

    candidate_seller_ids = [seller.user_id]
    if seller.user_id != 1:
        # Development fallback: show demo graphs from seller_1 when current seller has none.
        candidate_seller_ids.append(1)

    for candidate_seller_id in candidate_seller_ids:
        report_period, graph_paths = _get_graph_paths_for_seller(candidate_seller_id)
        if graph_paths:
            selected_seller_id = candidate_seller_id
            break

    if not graph_paths:
        raise HTTPException(404, "no analytics graph data found for this seller")

    graphs: list[AnalyticsGraph] = []
    for key in GRAPH_FILE_NAMES:
        path = graph_paths.get(key)
        if not path:
            continue
        try:
            image_data = base64.b64encode(path.read_bytes()).decode("ascii")
        except OSError as err:
            raise HTTPException(500, f"failed to read graph file: {path}") from err
        graphs.append(
            AnalyticsGraph(
                key=key,
                title=GRAPH_TITLES.get(key, key),
                image_data_url=f"data:image/png;base64,{image_data}",
            )
        )

    if not graphs:
        raise HTTPException(404, "analytics graphs are unavailable for this seller")

    return AnalyticsGraphsResponse(
        seller_user_id=selected_seller_id,
        report_period=report_period,
        graphs=graphs,
    )


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
