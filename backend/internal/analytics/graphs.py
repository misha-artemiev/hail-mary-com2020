"""Module for processing and formatting seller analytics data into graph points."""

from datetime import date, time

from pydantic import BaseModel

# --- INPUT MODELS ---


class CategoryMetrics(BaseModel):
    """Schema for category distribution data."""

    category_id: int
    collected_qty: int


class DailySalesMetrics(BaseModel):
    """Schema for daily sales and posting volume."""

    day: date
    sold_qty: int
    posted_qty: int


class TimeWindowMetrics(BaseModel):
    """Schema for distribution across pickup windows."""

    time_window: time  # Stored as a time object so 9:00 AM sorts before 10:00 AM
    collected_qty: int


# --- OUTPUT MODELS ---


class SalesGraphPoint(BaseModel):
    """Schema for sales vs. posted graph points."""

    day: date
    posted_qty: float
    sold_qty: float


class CategoryGraphPoint(BaseModel):
    """Schema for category distribution graph points."""

    collected_qty: float
    category_id: int


class TimeWindowGraphPoint(BaseModel):
    """Schema for time window distribution graph points."""

    collected_qty: float
    time_window: time


class GaugeGraphPoint(BaseModel):
    """Schema for a single percentage value (for a gauge/donut chart)."""

    sell_through_percentage: float


# --- THE ANALYTICS ENGINE ---


class SellerAnalytics:
    """Module for processing and formatting seller analytics data into graph points."""

    @staticmethod
    def graph_weekly_sales_vs_posted(
        daily_rows: list[DailySalesMetrics],
    ) -> list[SalesGraphPoint]:
        """Return coordinates for the provided days (Multi Line Graph)."""
        # Sort the days chronologically so the line graph draws left-to-right correctly.
        sorted_rows = sorted(daily_rows, key=lambda row: row.day)

        # Package the sorted data into our output format.
        return [
            SalesGraphPoint(
                # max(value, 0) is a safety net: if a database error ever returns
                # a negative number (-5 items), we force it to be 0
                # so the graph doesn't break.
                day=row.day,
                posted_qty=float(max(row.posted_qty, 0)),
                sold_qty=float(max(row.sold_qty, 0)),
            )
            for row in sorted_rows
        ]

    @staticmethod
    def graph_sell_through_rate(daily_rows: list[DailySalesMetrics]) -> GaugeGraphPoint:
        """Return the overall sell-through rate (Gauge/Donut Chart)."""
        # Add up all items posted and sold across the entire time period.
        total_posted = sum(max(row.posted_qty, 0) for row in daily_rows)
        total_sold = sum(max(row.sold_qty, 0) for row in daily_rows)

        # Prevent a "Division by Zero" crash if the seller didn't post anything.
        if total_posted == 0:
            return GaugeGraphPoint(sell_through_percentage=0.0)

        # Calculate the percentage.
        # We use min(..., 100.0) to cap it at 100% just in case a data glitch
        # e.g., says they sold 10 items but only posted 8.
        percentage = min((total_sold / total_posted) * 100.0, 100.0)

        # Round to 2 decimal places (e.g., 85.45) for frontend display.
        return GaugeGraphPoint(sell_through_percentage=round(percentage, 2))

    @staticmethod
    def graph_category_distribution(
        bundles: list[CategoryMetrics], top_n: int = 5
    ) -> list[CategoryGraphPoint]:
        """Return points for category distribution (Pie/Bar Chart)."""
        # if we don't want any results or have no data.
        if top_n <= 0 or not bundles:
            return []

        # Group all the raw rows together by their category ID.
        collected_by_category: dict[int, float] = {}
        for bundle in bundles:
            qty = float(max(bundle.collected_qty, 0))
            # If the category exists in the dictionary, add to it. Otherwise,
            # start at 0.0 and add.
            collected_by_category[bundle.category_id] = (
                collected_by_category.get(bundle.category_id, 0.0) + qty
            )

        # Sort the categories to find the top performers.
        # -item[1] means sort by the total quantity DESCENDING (biggest first).
        # item[0] is the tie-breaker: sort by Category ID ASCENDING.
        top_categories = sorted(
            collected_by_category.items(), key=lambda item: (-item[1], item[0])
        )[:top_n]  # The [:top_n] chops off everything except the top winners

        # Package the winners into the output format.
        return [
            CategoryGraphPoint(collected_qty=qty, category_id=cat_id)
            for cat_id, qty in top_categories
        ]

    @staticmethod
    def graph_time_window_distribution(
        time_windows: list[TimeWindowMetrics], top_n: int = 5
    ) -> list[TimeWindowGraphPoint]:
        """Return points for time-window distribution (Histogram/Bar Chart)."""
        # if we don't want any results or have no data.
        if top_n <= 0 or not time_windows:
            return []

        # Group the collections by their time window.
        collected_by_window: dict[time, float] = {}
        for window in time_windows:
            qty = float(max(window.collected_qty, 0))
            collected_by_window[window.time_window] = (
                collected_by_window.get(window.time_window, 0.0) + qty
            )

        # Sort by highest volume first.
        # Because we are using real 'time' objects, the tie-breaker (item[0])
        # correctly understands that 9:00 AM comes before 10:00 AM.
        top_windows = sorted(
            collected_by_window.items(), key=lambda item: (-item[1], item[0])
        )[:top_n]

        # Package into the output format.
        return [
            TimeWindowGraphPoint(collected_qty=qty, time_window=window)
            for window, qty in top_windows
        ]
