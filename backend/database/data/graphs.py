"""Graph generation for seller analytics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

# Headless-safe backend for local scripts/CI.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from database.data.DataAnalysis import DATA_DIR, seller_analytics
except ModuleNotFoundError:
    try:
        from DataAnalysis import DATA_DIR, seller_analytics
    except ModuleNotFoundError:
        from .DataAnalysis import DATA_DIR, seller_analytics


def _safe_rate(numerator: float, denominator: float) -> float:
    """Compute percentage rate with divide-by-zero guard."""
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def _derive_pickup_window_label(row: pd.Series) -> str:
    """Build fallback pickup-window label from bundle timestamps."""
    start = pd.to_datetime(row["window_start"])
    end = pd.to_datetime(row["window_end"])
    return f"{start:%H:%M}-{end:%H:%M}"


def plot_top_time_windows(
    analytics: dict[str, Any],
    seller_user_id: int,
    data_dir: Path,
    output_path: Path,
) -> Path:
    """Plot top 3 most used collection windows based on collected reservations."""
    report_period = analytics.get("report_period", {})
    bundles_df = pd.read_csv(
        data_dir / "bundles.csv", parse_dates=["window_start", "window_end"]
    )
    reservations_df = pd.read_csv(
        data_dir / "reservations.csv", parse_dates=["collected_at"]
    )
    week_start = pd.Timestamp(report_period["week_start"])
    week_end = pd.Timestamp(report_period["week_end"])

    weekly_bundles = bundles_df[
        (bundles_df["seller_id"] == seller_user_id)
        & (bundles_df["window_end"] >= week_start)
        & (bundles_df["window_end"] < week_end)
    ].copy()
    weekly_bundle_ids = set(weekly_bundles["bundle_id"].tolist())
    weekly_collected = reservations_df[
        (reservations_df["bundle_id"].isin(weekly_bundle_ids))
        & (reservations_df["status"] == "collected")
    ].copy()

    windows_df = weekly_collected.merge(
        weekly_bundles[
            ["bundle_id", "window_start", "window_end", "collection_time_label"]
            if "collection_time_label" in weekly_bundles.columns
            else ["bundle_id", "window_start", "window_end"]
        ],
        on="bundle_id",
        how="left",
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    if windows_df.empty:
        ax.text(
            0.5,
            0.5,
            "No collected reservations for selected week",
            ha="center",
            va="center",
        )
        ax.axis("off")
    else:
        if "collection_time_label" in windows_df.columns:
            windows_df["window_label"] = (
                windows_df["collection_time_label"].fillna("").astype(str).str.strip()
            )
        else:
            windows_df["window_label"] = ""
        fallback_label = (
            windows_df["window_start"].dt.strftime("%H:%M")
            + "-"
            + windows_df["window_end"].dt.strftime("%H:%M")
        )
        windows_df.loc[windows_df["window_label"] == "", "window_label"] = fallback_label

        top_windows = (
            windows_df.groupby("window_label")
            .size()
            .reset_index(name="collected_reservations")
            .sort_values("collected_reservations", ascending=False)
            .head(3)
        )
        ax.barh(
            top_windows["window_label"],
            top_windows["collected_reservations"],
            color="#2E86AB"
        )
        ax.invert_yaxis()
        for row in top_windows.itertuples(index=False):
            ax.text(
                row.collected_reservations + 0.05,
                row.window_label,
                f"{row.collected_reservations} collected",
                va="center",
                fontsize=9,
            )
        ax.set_title("Top 3 Most Used Collection Windows (Collected Reservations)")
        ax.set_xlabel("Collected reservations")
        ax.set_ylabel("Collection window")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def plot_sell_rate_capacity(
    analytics: dict[str, Any],
    seller_user_id: int,
    data_dir: Path,
    output_path: Path,
) -> Path:
    """Plot weekly reservation and actual sell rates vs bundle quantity capacity."""
    summary = analytics.get("summary", {})
    report_period = analytics.get("report_period", {})

    bundles_df = pd.read_csv(data_dir / "bundles.csv", parse_dates=["window_end"])
    week_start = pd.Timestamp(report_period["week_start"])
    week_end = pd.Timestamp(report_period["week_end"])

    weekly_bundles = bundles_df[
        (bundles_df["seller_id"] == seller_user_id)
        & (bundles_df["window_end"] >= week_start)
        & (bundles_df["window_end"] < week_end)
    ]
    total_bundle_quantity = int(weekly_bundles["total_qty"].sum())
    reservations = int(summary.get("total_reservations", 0))
    no_shows = int(summary.get("no_show_reservations", 0))
    capped_reservations = min(reservations, total_bundle_quantity)
    actual_sales = max(min(reservations - no_shows, total_bundle_quantity), 0)

    reservation_rate = _safe_rate(capped_reservations, total_bundle_quantity)
    actual_sell_rate = _safe_rate(actual_sales, total_bundle_quantity)

    fig, ax = plt.subplots(figsize=(9, 5))
    labels = ["Reservation rate", "Actual sell rate"]
    values = [reservation_rate, actual_sell_rate]
    bars = ax.bar(labels, values, color=["#F6C85F", "#6F4E7C"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Rate (%)")
    ax.set_title("Weekly Sell Rates vs Bundle Quantity Capacity", pad=22)
    ax.legend(
        bars,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.0),
        ncol=2,
        frameon=False,
        borderaxespad=0.2,
    )

    subtitle = (
        f"capacity={total_bundle_quantity} qty, reservations={reservations}, "
        f"no-shows={no_shows}, effective sales={actual_sales}"
    )
    ax.text(
        0.5,
        1.01,
        subtitle,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        clip_on=False,
    )

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def plot_top_categories(
    analytics: dict[str, Any],
    output_path: Path,
) -> Path:
    """Plot top 3 categories by reservations for the weekly report."""
    categories_df = pd.DataFrame(analytics.get("top_categories", []))

    fig, ax = plt.subplots(figsize=(9, 5))
    if categories_df.empty:
        ax.text(0.5, 0.5, "No weekly category data", ha="center", va="center")
        ax.axis("off")
    else:
        top_categories = categories_df.sort_values("reservations", ascending=False).head(3)
        bars = ax.bar(
            top_categories["category_name"],
            top_categories["reservations"],
            color="#9FD356",
            label="Reservations",
        )
        for row in top_categories.itertuples(index=False):
            details = (
                f"collected={row.collected}, "
                f"no-show={row.no_show}, reserved={row.reserved}"
            )
            ax.text(
                row.category_name,
                row.reservations + 0.1,
                details,
                ha="center",
                va="bottom",
                fontsize=9,
            )
        ax.set_title("Top 3 Categories by Reservations (Weekly)", pad=22)
        ax.legend(
            [bars[0]],
            ["Reservations"],
            loc="upper center",
            bbox_to_anchor=(0.5, 1.0),
            ncol=1,
            frameon=False,
            borderaxespad=0.2,
        )
        ax.set_ylabel("Reservations")
        ax.set_xlabel("Category")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    return output_path


def generate_seller_weekly_graphs(
    seller_user_id: int,
    week_start: str | None = None,
    data_dir: Path = DATA_DIR,
    output_dir: Path | None = None,
) -> dict[str, str]:
    """Generate all seller analytics graphs and return their file paths."""
    analytics = seller_analytics(
        seller_user_id=seller_user_id, data_dir=data_dir, week_start=week_start
    )
    if week_start is None and analytics.get("summary", {}).get("collected_reservations", 0) == 0:
        bundles_df = pd.read_csv(data_dir / "bundles.csv", parse_dates=["window_end"])
        reservations_df = pd.read_csv(data_dir / "reservations.csv", parse_dates=["collected_at"])
        seller_bundle_ids = set(
            bundles_df[bundles_df["seller_id"] == seller_user_id]["bundle_id"].tolist()
        )
        seller_collected = reservations_df[
            (reservations_df["bundle_id"].isin(seller_bundle_ids))
            & (reservations_df["status"] == "collected")
            & reservations_df["collected_at"].notna()
        ]
        if not seller_collected.empty:
            latest_collected = seller_collected["collected_at"].max().normalize()
            inferred_week_start = latest_collected - pd.Timedelta(days=latest_collected.weekday())
            analytics = seller_analytics(
                seller_user_id=seller_user_id,
                data_dir=data_dir,
                week_start=inferred_week_start,
            )
    period = analytics["report_period"]
    week_key = period["week_start"][:10]

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "graphs" / f"seller_{seller_user_id}" / week_key

    top_windows_path = plot_top_time_windows(
        analytics, seller_user_id, data_dir, output_dir / "top_time_windows.png"
    )
    sell_rate_path = plot_sell_rate_capacity(
        analytics, seller_user_id, data_dir, output_dir / "sell_rate_capacity.png"
    )
    top_categories_path = plot_top_categories(
        analytics, output_dir / "top_categories.png"
    )

    return {
        "top_time_windows": str(top_windows_path),
        "sell_rate_capacity": str(sell_rate_path),
        "top_categories": str(top_categories_path),
    }


if __name__ == "__main__":
    paths = generate_seller_weekly_graphs(seller_user_id=1)
    print(paths)
