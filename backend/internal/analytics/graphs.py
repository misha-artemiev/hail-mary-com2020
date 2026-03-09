# ROUGH INTERFACE EXAMPLE
from datetime import date

from pydantic import BaseModel

class SellerAnalytics():

    def SellerAnalytics(self, consumer_id: int):
        """Basic init information needed for all greaphs."""
        self.consumer = consumer_id # if needed at all
        ...

    class GraphCategoryDistriutionBundlesModel(BaseModel):
        category: int # or categories: [int]
        reservations: int # number of reservations
        collected: int # how many reservations were actually collected
        ...

    class DailySalesBundlesModel(BaseModel):
        seller_id: int
        day: date
        sold_qty: int
        posted_qty: int

    def graph_weekly_sales_vs_posted(
        self,
        seller_id: int,
        analysis_days: list[date],
        daily_rows: list["SellerAnalytics.DailySalesBundlesModel"],
    ) -> list[tuple[float, float]]:
        """Return coordinates for the requested days for one seller.

        x: number of posted bundles for a day
        y: number of sold bundles for that day
        analysis_days controls which days are returned and in what order.
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

    def graph_category_distribution(
        self,
        bundles: list["SellerAnalytics.GraphCategoryDistriutionBundlesModel"],
    ) -> list[tuple[float, int]]:
        """Return points for category distribution.

        x: number of collected bundles for the category
        y: corresponding category id

        Returns only the top 5 categories by collected bundles.
        """
        collected_by_category: dict[int, float] = {}
        for bundle in bundles:
            collected_qty = float(max(bundle.collected, 0))
            collected_by_category[bundle.category] = (
                collected_by_category.get(bundle.category, 0.0) + collected_qty
            )

        top_categories = sorted(
            collected_by_category.items(),
            key=lambda item: (-item[1], item[0]),
        )[:5]

        graph_points: list[tuple[float, int]] = []
        for category, collected_qty in top_categories:
            graph_points.append((collected_qty, category))

        return graph_points
