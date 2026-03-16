"""Graph refreshing background processing."""

from fastapi import BackgroundTasks, HTTPException, status
from internal.analytics.graphs import BundleRow, ReservationRow, SellerAnalytics
from internal.database.manager import database_manager
from internal.queries.analytics import AsyncQuerier as AnalyticsQuerier
from internal.queries.analytics import CreateGraphParams, GetGraphParams
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.reservations import AsyncQuerier as ReservationQuerier


class AnalyticsProcesser:
    """Analytics processing."""

    background_tasks: BackgroundTasks

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        """Init processing for seller."""
        self.background_tasks = background_tasks

    def run(self, seller_id: int) -> None:
        """Starts background analytics task.

        Args:
            seller_id: seller id
        """
        self.background_tasks.add_task(self.process_analytics, seller_id)

    @staticmethod
    async def process_analytics(seller_id: int) -> None:
        """Background graph processing.

        Args:
            seller_id: seller_id

        Raises:
            ValueError: failed to process graphs
        """
        async for conn in database_manager.get_connection():
            analytics_querier = AnalyticsQuerier(conn)
            graph_types = analytics_querier.get_graphs_types()
            async for graph_type in graph_types:
                if (
                    graph := await analytics_querier.get_graph(
                        GetGraphParams(
                            seller_id=seller_id, graph_type=graph_type.graph_type_id
                        )
                    )
                ) is not None:
                    analytics_querier.delete_graph_series(graph_id=graph.graph_id)
                if (
                    await analytics_querier.create_graph(
                        CreateGraphParams(
                            seller_id=seller_id, graph_type=graph_type.graph_type_id
                        )
                    )
                    is None
                ):
                    raise ValueError("Failed to create analytics graph")
            if (
                seller_bundles := BundleQuerier(conn).get_sellers_bundles(
                    seller_id=seller_id
                )
            ) is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "failed to get seller bundles",
                )
            if (
                seller_reservations := ReservationQuerier(
                    conn
                ).get_seller_reservations_full(seller_id=seller_id)
            ) is None:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "failed to get seller reservations",
                )
            bundle_rows = [
                BundleRow(
                    bundle_date=bundle.window_start.date(), total_qty=bundle.total_qty
                )
                async for bundle in seller_bundles
            ]
            reservation_rows = [
                ReservationRow(
                    bundle_date=reservation.window_start.date(),
                    window_start=reservation.window_start.time(),
                    category_id=...,
                    collected_at=reservation.collected_at,
                )
                async for reservation in seller_reservations
            ]
            # weekly sales vs posted (multi line)
            for points in SellerAnalytics.graph_weekly_sales_vs_posted():
                pass
            # sell through rate (pie)
            for points in SellerAnalytics.graph_sell_through_rate():
                pass
            # category distribution (pie/bar)
            for points in SellerAnalytics.graph_category_distribution():
                pass
            # time window distribution (pie/bar)
            for points in SellerAnalytics.graph_time_window_distribution():
                pass
