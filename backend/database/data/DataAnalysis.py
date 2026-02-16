"""Seller analytics on top of generated synthetic CSV files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "synthetic_data"
STATUS_COLLECTED = "collected"
STATUS_NO_SHOW = "no_show"
STATUS_RESERVED = "reserved"


def _load_tables(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Load all CSV inputs needed for seller analytics."""
    bundles = pd.read_csv(
        data_dir / "bundles.csv", parse_dates=["window_start", "window_end", "created_at"]
    )
    reservations = pd.read_csv(
        data_dir / "reservations.csv", parse_dates=["reserved_at", "collected_at"]
    )
    sellers = pd.read_csv(data_dir / "sellers.csv")
    categories = pd.read_csv(data_dir / "category.csv")
    bundle_categories = pd.read_csv(data_dir / "bundle_category.csv")
    return {
        "bundles": bundles,
        "reservations": reservations,
        "sellers": sellers,
        "categories": categories,
        "bundle_categories": bundle_categories,
    }


def _bundle_outcome(
    statuses: set[str],
    window_end: pd.Timestamp,
    now: pd.Timestamp,
) -> str:
    """Classify a posted bundle into one outcome bucket."""
    if STATUS_COLLECTED in statuses:
        return STATUS_COLLECTED
    if STATUS_NO_SHOW in statuses:
        return STATUS_NO_SHOW
    if STATUS_RESERVED in statuses and window_end < now:
        return "expired"
    if STATUS_RESERVED in statuses:
        return "reserved_open"
    return "unreserved"


def _build_bundle_outcomes(
    seller_bundles: pd.DataFrame,
    seller_reservations: pd.DataFrame,
) -> pd.DataFrame:
    """Attach one outcome label to every bundle posted by the seller."""
    now = pd.Timestamp.now()
    status_by_bundle = (
        seller_reservations.groupby("bundle_id")["status"]
        .apply(lambda values: set(values.tolist()))
        .to_dict()
    )

    outcome_rows: list[dict[str, Any]] = []
    for row in seller_bundles.itertuples(index=False):
        statuses = status_by_bundle.get(row.bundle_id, set())
        outcome_rows.append({
            "bundle_id": row.bundle_id,
            "seller_id": row.seller_id,
            "discount_percentage": row.discount_percentage,
            "window_start": row.window_start,
            "window_end": row.window_end,
            "pickup_window": f"{row.window_start:%H:%M}-{row.window_end:%H:%M}",
            "outcome": _bundle_outcome(statuses, row.window_end, now),
        })
    return pd.DataFrame(outcome_rows)


def seller_analytics(seller_user_id: int, data_dir: Path = DATA_DIR) -> dict[str, Any]:
    """Compute analytics for a seller by `user_id`."""
    data = _load_tables(data_dir)
    bundles = data["bundles"]
    reservations = data["reservations"]
    sellers = data["sellers"]
    categories = data["categories"]
    bundle_categories = data["bundle_categories"]

    seller = sellers[sellers["user_id"] == seller_user_id]
    if seller.empty:
        raise ValueError(f"Seller user_id={seller_user_id} not found.")

    seller_name = str(seller.iloc[0]["seller_name"])
    seller_bundles = bundles[bundles["seller_id"] == seller_user_id].copy()
    if seller_bundles.empty:
        return {
            "seller_user_id": seller_user_id,
            "seller_name": seller_name,
            "summary": {"total_bundles_posted": 0, "total_reservations": 0},
            "sell_through": {},
            "pricing_effectiveness": [],
            "pickup_window_performance": [],
            "top_categories": [],
            "waste_proxy": {
                "implemented": False,
                "note": "Pending agreement on average bundle weight estimation strategy.",
            },
        }

    seller_bundle_ids = seller_bundles["bundle_id"]
    seller_reservations = reservations[reservations["bundle_id"].isin(seller_bundle_ids)].copy()

    bundle_outcomes = _build_bundle_outcomes(seller_bundles, seller_reservations)
    total_posted = int(len(bundle_outcomes))
    outcome_counts = bundle_outcomes["outcome"].value_counts().to_dict()

    collected_bundles = int(outcome_counts.get(STATUS_COLLECTED, 0))
    no_show_bundles = int(outcome_counts.get(STATUS_NO_SHOW, 0))
    expired_bundles = int(outcome_counts.get("expired", 0))
    reserved_open_bundles = int(outcome_counts.get("reserved_open", 0))
    unreserved_bundles = int(outcome_counts.get("unreserved", 0))

    total_reservations = int(len(seller_reservations))
    collected_reservations = int((seller_reservations["status"] == STATUS_COLLECTED).sum())
    no_show_reservations = int((seller_reservations["status"] == STATUS_NO_SHOW).sum())
    reserved_reservations = int((seller_reservations["status"] == STATUS_RESERVED).sum())

    sell_through = {
        "collected_bundle_rate": round(collected_bundles / total_posted, 4),
        "no_show_bundle_rate": round(no_show_bundles / total_posted, 4),
        "expired_bundle_rate": round(expired_bundles / total_posted, 4),
        "reserved_open_bundle_rate": round(reserved_open_bundles / total_posted, 4),
        "unreserved_bundle_rate": round(unreserved_bundles / total_posted, 4),
    }

    pricing = (
        bundle_outcomes.groupby("discount_percentage")
        .agg(
            posted_bundles=("bundle_id", "count"),
            collected_bundles=("outcome", lambda values: (values == STATUS_COLLECTED).sum()),
            no_show_bundles=("outcome", lambda values: (values == STATUS_NO_SHOW).sum()),
            expired_bundles=("outcome", lambda values: (values == "expired").sum()),
        )
        .reset_index()
        .sort_values("discount_percentage")
    )
    pricing["sell_through_rate"] = (
        pricing["collected_bundles"] / pricing["posted_bundles"]
    ).round(4)

    windows = (
        bundle_outcomes.groupby("pickup_window")
        .agg(
            posted_bundles=("bundle_id", "count"),
            collected_bundles=("outcome", lambda values: (values == STATUS_COLLECTED).sum()),
            no_show_bundles=("outcome", lambda values: (values == STATUS_NO_SHOW).sum()),
            expired_bundles=("outcome", lambda values: (values == "expired").sum()),
        )
        .reset_index()
    )
    windows["sell_through_rate"] = (windows["collected_bundles"] / windows["posted_bundles"]).round(4)
    windows = windows.sort_values(
        ["sell_through_rate", "posted_bundles"], ascending=[False, False]
    )

    category_map = bundle_categories.merge(categories, on="category_id", how="left")
    seller_categories = category_map[category_map["bundle_id"].isin(seller_bundle_ids)].copy()
    seller_categories = seller_categories.merge(
        seller_reservations[["reservation_id", "bundle_id", "status"]],
        on="bundle_id",
        how="left",
    )
    seller_categories = seller_categories.drop_duplicates(
        subset=["reservation_id", "category_id"]
    )

    category_popularity = (
        seller_categories.groupby("category_name")
        .agg(
            reservations=("reservation_id", "count"),
            collected=("status", lambda values: (values == STATUS_COLLECTED).sum()),
            no_show=("status", lambda values: (values == STATUS_NO_SHOW).sum()),
            reserved=("status", lambda values: (values == STATUS_RESERVED).sum()),
        )
        .reset_index()
        .sort_values("reservations", ascending=False)
    )

    summary = {
        "total_bundles_posted": total_posted,
        "total_reservations": total_reservations,
        "collected_reservations": collected_reservations,
        "no_show_reservations": no_show_reservations,
        "reserved_reservations": reserved_reservations,
    }

    return {
        "seller_user_id": seller_user_id,
        "seller_name": seller_name,
        "summary": summary,
        "sell_through": sell_through,
        "pricing_effectiveness": pricing.to_dict(orient="records"),
        "pickup_window_performance": windows.to_dict(orient="records"),
        "top_categories": category_popularity.to_dict(orient="records"),
        "waste_proxy": {
            "implemented": False,
            "note": "Pending agreement on average bundle weight estimation strategy.",
        },
    }


if __name__ == "__main__":
    result = seller_analytics(seller_user_id=1)
    print("Summary:", result["summary"])
    print("Sell-through:", result["sell_through"])
    print("Top pickup windows:", result["pickup_window_performance"][:3])
    print("Top categories:", result["top_categories"][:3])
