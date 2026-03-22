"""Graph refreshing background processing."""

from decimal import Decimal

from fastapi import BackgroundTasks
from internal.analytics.graphs import BundleRow, ReservationRow, SellerAnalytics
from internal.database.manager import database_manager
from internal.logger.logger import logger
from internal.queries.analytics import AsyncQuerier as AnalyticsQuerier
from internal.queries.analytics import (
    CreateGraphParams,
    CreateGraphPointParams,
    CreateGraphSeriesParams,
    GetGraphParams,
)
from internal.queries.bundle import AsyncQuerier as BundleQuerier
from internal.queries.category import AsyncQuerier as CategoryQuerier
from internal.queries.reservations import AsyncQuerier as ReservationQuerier
from sqlalchemy.ext.asyncio import AsyncConnection


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
    async def add_sales_vs_posted_graph(
        analytics_querier: AnalyticsQuerier,
        seller_id: int,
        bundle_rows: list[BundleRow],
        reservation_rows: list[ReservationRow],
    ) -> None:
        """Add seles vs posted graph.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            bundle_rows: formatted bundle rows
            reservation_rows: formatted reservation rows
        """
        if (
            graph := await analytics_querier.get_graph(
                GetGraphParams(seller_id=seller_id, graph_type=1)
            )
        ) is None:
            logger.exception("failed to get seles_vs_posted graph")
            return
        if (
            sales_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="sales", sort_index=0
                )
            )
        ) is None:
            logger.exception("failed to create sales series for sales_vs_posted")
            return
        if (
            posted_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="posted", sort_index=1
                )
            )
        ) is None:
            logger.exception("failed to create posted series for sales_vs_posted")
            return
        for i, point in enumerate(
            SellerAnalytics.graph_weekly_sales_vs_posted(bundle_rows, reservation_rows)
        ):
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=sales_series.series_id,
                        sort_index=i,
                        x=point.day.strftime("%Y-%m-%d"),
                        y=Decimal(point.sold_qty),
                    )
                )
                is None
            ):
                logger.exception(
                    "failed to create point for sales series for sales_vs_posted"
                )
                return
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=posted_series.series_id,
                        sort_index=i,
                        x=point.day.strftime("%Y-%m-%d"),
                        y=Decimal(point.posted_qty),
                    )
                )
                is None
            ):
                logger.exception(
                    "failed to create point for sales series for sales_vs_posted"
                )
                return

    @staticmethod
    async def add_sell_through_rate_graph(
        analytics_querier: AnalyticsQuerier,
        seller_id: int,
        bundle_rows: list[BundleRow],
        reservation_rows: list[ReservationRow],
    ) -> None:
        """Add sell through rate graph.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            bundle_rows: formatted bundle rows
            reservation_rows: formatted reservation rows
        """
        if (
            graph := await analytics_querier.get_graph(
                GetGraphParams(seller_id=seller_id, graph_type=2)
            )
        ) is None:
            logger.exception("failed to get sell_through_rate graph")
            return
        if (
            sell_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="sell_rate", sort_index=0
                )
            )
        ) is None:
            logger.exception("failed to create sell series for sell_through_rate graph")
            return
        sell_through_rate = SellerAnalytics.graph_sell_through_rate(
            bundle_rows, reservation_rows
        ).sell_through_percentage
        if (
            await analytics_querier.create_graph_point(
                CreateGraphPointParams(
                    series_id=sell_series.series_id,
                    sort_index=0,
                    x="sold",
                    y=Decimal(sell_through_rate),
                )
            )
        ) is None:
            logger.exception("failed to create sold point for sell_through_rate graph")
            return
        if (
            await analytics_querier.create_graph_point(
                CreateGraphPointParams(
                    series_id=sell_series.series_id,
                    sort_index=1,
                    x="unsold",
                    y=Decimal(100 - sell_through_rate),
                )
            )
        ) is None:
            logger.exception(
                "failed to create unsold point for sell_through_rate graph"
            )
            return

    @staticmethod
    async def add_cateogry_distribution_graph(
        analytics_querier: AnalyticsQuerier,
        seller_id: int,
        reservation_rows: list[ReservationRow],
        conn: AsyncConnection,
    ) -> None:
        """Add category distribution graph.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            reservation_rows: formatted reservation rows
            conn: database connection
        """
        if (
            graph := await analytics_querier.get_graph(
                GetGraphParams(seller_id=seller_id, graph_type=3)
            )
        ) is None:
            logger.exception("failed to get category_distribution graph")
            return
        if (
            categories_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="categories", sort_index=0
                )
            )
        ) is None:
            logger.exception(
                "failed to create categories series for category_distribution graph"
            )
            return
        category_distribution = SellerAnalytics.graph_category_distribution(
            reservation_rows
        )
        category_querier = CategoryQuerier(conn)
        for i, category in enumerate(category_distribution):
            if (
                category_row := await category_querier.get_category(
                    category_id=category.category_id
                )
            ) is None:
                logger.exception("failed to get category")
                return
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=categories_series.series_id,
                        sort_index=i,
                        x=category_row.category_name,
                        y=Decimal(category.collected_qty),
                    )
                )
            ) is None:
                logger.exception(
                    "failed to create category point for category_distribution graph"
                )
                return

    @staticmethod
    async def add_time_window_distribution_graph(
        analytics_querier: AnalyticsQuerier,
        seller_id: int,
        reservation_rows: list[ReservationRow],
    ) -> None:
        """Add time window distribution graph.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            reservation_rows: formatted reservation rows
        """
        if (
            graph := await analytics_querier.get_graph(
                GetGraphParams(seller_id=seller_id, graph_type=4)
            )
        ) is None:
            logger.exception("failed to get time_window_distribution graph")
            return
        if (
            time_windows_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="time_windows", sort_index=0
                )
            )
        ) is None:
            logger.exception("failed to create time_windows series")
            return
        time_windows_distribution = SellerAnalytics.graph_time_window_distribution(
            reservation_rows
        )
        for i, time_window in enumerate(time_windows_distribution):
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=time_windows_series.series_id,
                        sort_index=i,
                        x=time_window.time_window.strftime("%H:%M"),
                        y=Decimal(time_window.collected_qty),
                    )
                )
            ) is None:
                logger.exception("failed to create time_window point")
                return

    @staticmethod
    async def add_forecast_graph(
        analytics_querier: AnalyticsQuerier,
        seller_id: int,
        bundle_rows: list[BundleRow],
        reservation_rows: list[ReservationRow],
    ) -> None:
        """Add forecast vs posted graph.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            bundle_rows: formatted bundle rows
            reservation_rows: formatted reservation rows
        """
        if (
            graph := await analytics_querier.get_graph(
                GetGraphParams(seller_id=seller_id, graph_type=5)
            )
        ) is None:
            logger.exception("failed to get forecast graph")
            return
        if (
            sales_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="sales", sort_index=0
                )
            )
        ) is None:
            logger.exception("failed to create sales series for forecast")
            return
        if (
            posted_series := await analytics_querier.create_graph_series(
                CreateGraphSeriesParams(
                    graph_id=graph.graph_id, series_name="posted", sort_index=1
                )
            )
        ) is None:
            logger.exception("failed to create posted series for forecast")
            return
        for i, point in enumerate(
            SellerAnalytics.graph_weekly_sales_vs_posted(bundle_rows, reservation_rows)
        ):
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=sales_series.series_id,
                        sort_index=i,
                        x=point.day.strftime("%Y-%m-%d"),
                        y=Decimal(point.sold_qty),
                    )
                )
                is None
            ):
                logger.exception("failed to create point for sales series for forecast")
                return
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=posted_series.series_id,
                        sort_index=i,
                        x=point.day.strftime("%Y-%m-%d"),
                        y=Decimal(point.posted_qty),
                    )
                )
                is None
            ):
                logger.exception(
                    "failed to create point for posted series for forecast"
                )
                return

    @staticmethod
    async def process_analytics(seller_id: int) -> None:
        """Background graph processing.

        Args:
            seller_id: seller_id

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
                    await analytics_querier.delete_graph_series(graph_id=graph.graph_id)
                elif (
                    await analytics_querier.create_graph(
                        CreateGraphParams(
                            seller_id=seller_id, graph_type=graph_type.graph_type_id
                        )
                    )
                    is None
                ):
                    logger.exception("Failed to create analytics graph")
                    return
            seller_bundles = BundleQuerier(conn).get_sellers_bundles(
                seller_id=seller_id
            )
            seller_reservations = ReservationQuerier(conn).get_seller_reservations_full(
                seller_id=seller_id
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
                    category_ids=reservation.category_ids,
                    collected_at=reservation.collected_at,
                )
                async for reservation in seller_reservations
            ]
            await AnalyticsProcesser.add_sales_vs_posted_graph(
                analytics_querier, seller_id, bundle_rows, reservation_rows
            )
            await AnalyticsProcesser.add_sell_through_rate_graph(
                analytics_querier, seller_id, bundle_rows, reservation_rows
            )
            await AnalyticsProcesser.add_cateogry_distribution_graph(
                analytics_querier, seller_id, reservation_rows, conn
            )
            await AnalyticsProcesser.add_time_window_distribution_graph(
                analytics_querier, seller_id, reservation_rows
            )
            await AnalyticsProcesser.add_forecast_graph(
                analytics_querier, seller_id, bundle_rows, reservation_rows
            )
