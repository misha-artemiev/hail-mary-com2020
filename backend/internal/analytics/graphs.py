"""Module for processing and formatting seller analytics data into graph points."""

from datetime import date

from pydantic import BaseModel


class SellerAnalytics:
    """Module for processing and formatting seller analytics data into graph points."""
    def __init__(self, consumer_id: int | None = None) -> None:
        """Initialize the analytics processor.

        Args:
            consumer_id: Optional ID of the consumer for personalized analytics.
        """
        self.consumer_id = consumer_id

    class CategoryDistributionRow(BaseModel):
        """Schema for category distribution data."""

        category: int
        collected: int

    class DailySalesRow(BaseModel):
        """Schema for daily sales and posting volume."""

        seller_id: int
        day: date
        sold_qty: int
        posted_qty: int

    class TimeWindowDistributionRow(BaseModel):
        """Schema for distribution across pickup windows."""

        time_window: str
        collected: int

    # Backward-compatible aliases for older names.
    GraphCategoryDistriutionBundlesModel = CategoryDistributionRow
    DailySalesBundlesModel = DailySalesRow
    GraphTimeWindowDistributionBundlesModel = TimeWindowDistributionRow

    @staticmethod
    def graph_weekly_sales_vs_posted(
        seller_id: int,
        analysis_days: list[date],
        daily_rows: list[SellerAnalytics.DailySalesRow],
    ) -> list[tuple[float, float]]:
        """Return coordinates for the requested days for one seller.

        Args:
            seller_id: The ID of the seller to analyze.
            analysis_days: Dates to include in the graph.
            daily_rows: Raw data rows from the database.

        Returns:
            List of tuples (posted_qty, sold_qty) as floats.
        """
        requested_days = set(analysis_days)
        seller_rows = [
            row for row in daily_rows
            if row.seller_id == seller_id and row.day in requested_days
        ]
        rows_by_day = {row.day: row for row in seller_rows}

        graph_points: list[tuple[float, float]] = []
        for day in analysis_days:
            row = rows_by_day.get(day)
            posted_qty = 0.0 if row is None else float(max(row.posted_qty, 0))
            sold_qty = 0.0 if row is None else float(max(row.sold_qty, 0))
            graph_points.append((posted_qty, sold_qty))

        return graph_points

    @staticmethod
    def graph_category_distribution(
        bundles: list[SellerAnalytics.CategoryDistributionRow],
        top_n: int = 5,
    ) -> list[tuple[float, int]]:
        """Return points for category distribution.

        Args:
            bundles: Data rows for category analytics.
            top_n: Number of top categories to return.

        Returns:
            List of tuples (collected_qty, category_id).
        """
        if top_n <= 0:
            return []

        collected_by_category: dict[int, float] = {}
        for bundle in bundles:
            collected_qty = float(max(bundle.collected, 0))
            collected_by_category[bundle.category] = (
                collected_by_category.get(bundle.category, 0.0) + collected_qty
            )

        top_categories = sorted(
            collected_by_category.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top_n]
        return [(collected_qty, category) for category, collected_qty in top_categories]

    @staticmethod
    def graph_time_window_distribution(
        time_windows: list[SellerAnalytics.TimeWindowDistributionRow],
        top_n: int = 5,
    ) -> list[tuple[float, str]]:
        """Return points for time-window distribution.

        Args:
            time_windows: Data rows for time window analytics.
            top_n: Number of top windows to return.

        Returns:
            List of tuples (collected_qty, time_window).
        """
        if top_n <= 0:
            return []

        collected_by_window: dict[str, float] = {}
        for window in time_windows:
            collected_qty = float(max(window.collected, 0))
            collected_by_window[window.time_window] = (
                collected_by_window.get(window.time_window, 0.0) + collected_qty
            )

        top_windows = sorted(
            collected_by_window.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top_n]
        return [(collected_qty, time_window) for time_window, collected_qty in
                top_windows]
