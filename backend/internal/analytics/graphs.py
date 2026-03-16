"""Module for processing and formatting seller analytics data into graph points."""

from datetime import date, datetime, time

from pydantic import BaseModel

# --- INPUT MODELS ---


class BundleRow(BaseModel):
    """Schema for a raw bundle row."""

    # The date the pickup window falls on.
    bundle_date: date

    # How many slots the seller made available for this bundle.
    # This is what we count as "posted" on the sales and gauge graphs.
    total_qty: int


class ReservationRow(BaseModel):
    """Schema for a raw reservation row."""

    # The date of the bundle this reservation belongs to.
    bundle_date: date

    # The time window the bundle's pickup opens, used for the histogram.
    # Stored as a time object so 9:00 AM sorts correctly before 10:00 AM.
    window_start: time

    # The category the bundle belongs to, used for the category distribution.
    category_ids: list[int]

    # None means the consumer never showed up (no-show).
    # A timestamp means they collected their bundle (sale).
    collected_at: datetime | None


# --- OUTPUT MODELS ---


class SalesGraphPoint(BaseModel):
    """Schema for sales vs. posted graph points."""

    day: date
    posted_qty: float
    sold_qty: float


class CategoryGraphPoint(BaseModel):
    """Schema for category distribution graph points."""

    category_id: int
    collected_qty: float


class TimeWindowGraphPoint(BaseModel):
    """Schema for time window distribution graph points."""

    time_window: time
    collected_qty: float


class GaugeGraphPoint(BaseModel):
    """Schema for a single percentage value (for a gauge/donut chart)."""

    sell_through_percentage: float


# --- THE ANALYTICS ENGINE ---


class SellerAnalytics:
    """Module for processing and formatting seller analytics data into graph points."""

    @staticmethod
    def graph_weekly_sales_vs_posted(
        bundles: list[BundleRow], reservations: list[ReservationRow]
    ) -> list[SalesGraphPoint]:
        """Return coordinates for the provided days (Line Graph)."""
        # Group total posted slots by day from the bundles list.
        posted_by_day: dict[date, float] = {}
        for bundle in bundles:
            current = posted_by_day.get(bundle.bundle_date, 0.0)
            # max(value, 0) is a safety net: if a database error ever returns
            # a negative total_qty, we force it to 0 so the graph doesn't break.
            posted_by_day[bundle.bundle_date] = current + float(
                max(bundle.total_qty, 0)
            )

        # Count collected reservations by day from the reservations list.
        sold_by_day: dict[date, float] = {}
        for reservation in reservations:
            # Make sure every day from bundles has a sold entry even if zero sales
            # happened, so it still appears as a point on the line graph.
            if reservation.bundle_date not in sold_by_day:
                sold_by_day[reservation.bundle_date] = 0.0
            # Business rule: a reservation is a sale if the consumer actually
            # collected it (collected_at is not None).
            if reservation.collected_at is not None:
                sold_by_day[reservation.bundle_date] += 1.0

        # Merge both day-sets and sort chronologically so the line draws left-to-right.
        all_days = sorted(set(posted_by_day) | set(sold_by_day))
        return [
            SalesGraphPoint(
                day=day,
                posted_qty=posted_by_day.get(day, 0.0),
                sold_qty=sold_by_day.get(day, 0.0),
            )
            for day in all_days
        ]

    @staticmethod
    def graph_sell_through_rate(
        bundles: list[BundleRow], reservations: list[ReservationRow]
    ) -> GaugeGraphPoint:
        """Return the overall sell-through rate (Gauge/Donut Chart)."""
        # Add up all slots posted across all bundles.
        total_posted = sum(float(max(b.total_qty, 0)) for b in bundles)

        # Add up all collected reservations.
        total_sold = sum(1.0 for r in reservations if r.collected_at is not None)

        # Prevent a "Division by Zero" crash if the seller didn't post anything.
        if not total_posted:
            return GaugeGraphPoint(sell_through_percentage=0.0)

        # Calculate the percentage.
        # We use min(..., 100.0) to cap it at 100% just in case a data glitch
        # says they sold 10 items but only posted 8.
        percentage = min((total_sold / total_posted) * 100.0, 100.0)

        # Round to 2 decimal places (e.g., 85.45) for frontend display.
        return GaugeGraphPoint(sell_through_percentage=round(percentage, 2))

    @staticmethod
    def graph_category_distribution(
        reservations: list[ReservationRow], top_n: int = 5
    ) -> list[CategoryGraphPoint]:
        """Return points for category distribution (Pie/Bar Chart)."""
        # If we don't want any results or have no data.
        if top_n <= 0 or not reservations:
            return []

        # Count collected reservations per category.
        collected_by_category: dict[int, float] = {}
        for reservation in reservations:
            # Skip reservations that were not collected.
            if reservation.collected_at is None:
                continue
            # A bundle can belong to multiple categories.
            for category_id in reservation.category_ids:
                collected_by_category[category_id] = (
                    collected_by_category.get(category_id, 0.0) + 1.0
                )

        # Sort the categories to find the top ones.
        # -item[1] means sort by total collected DESCENDING (biggest first).
        # item[0] is the tie-breaker: sort by category_id ASCENDING.
        top_categories = sorted(
            collected_by_category.items(), key=lambda item: (-item[1], item[0])
        )[:top_n]  # The [:top_n] chops off everything except the top winners

        # Package the winners into the output format.
        return [
            CategoryGraphPoint(category_id=cat_id, collected_qty=qty)
            for cat_id, qty in top_categories
        ]

    @staticmethod
    def graph_time_window_distribution(
        reservations: list[ReservationRow], top_n: int = 5
    ) -> list[TimeWindowGraphPoint]:
        """Return points for time-window distribution (Histogram/Bar Chart)."""
        # If we don't want any results or have no data.
        if top_n <= 0 or not reservations:
            return []

        # Count collected reservations per time window.
        collected_by_window: dict[time, float] = {}
        for reservation in reservations:
            # Business rule: only collected reservations count toward a time window.
            if reservation.collected_at is None:
                continue
            collected_by_window[reservation.window_start] = (
                collected_by_window.get(reservation.window_start, 0.0) + 1.0
            )

        # Sort by highest volume first.
        # Because we are using real 'time' objects, the tie-breaker (item[0])
        # correctly understands that 9:00 AM comes before 10:00 AM.
        top_windows = sorted(
            collected_by_window.items(), key=lambda item: (-item[1], item[0])
        )[:top_n]

        # Package into the output format.
        return [
            TimeWindowGraphPoint(time_window=window, collected_qty=qty)
            for window, qty in top_windows
        ]
