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

    def graph_category_distribution(self, bundles: "SellerAnalytics.GraphCategoryDistriutionBundlesModel") -> list[tuple[float,float]]: # list of x and y tuples
        # some calcualtions/function calls
        return graph_points

    ...

    # just request data that is needed, it will result in smaller ram footprint

    # for graphs:
    # line: x and y of points
    # bar chart: x for cetegory/allergen/etc index and y for y
    # pie chart: x for category/allergen/etc index and y for percentage of a pie chart
    # multiline graph: not certain at this point, possible solution is to have a separate function for each line of the graph with graph_name_line_name() 
