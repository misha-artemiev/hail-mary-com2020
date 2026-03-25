"""Graph refreshing background processing."""

import datetime
from decimal import Decimal

from fastapi import BackgroundTasks
from internal.analytics.forecast import ForecastQuery, generate_seller_forecasts
from internal.analytics.forecast_info import BundleDetails, build_forecast_query
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
from internal.queries.forecast import AsyncQuerier as ForecastQuerier
from internal.queries.forecast import UpsertForecastOutputParams
from internal.queries.reservations import AsyncQuerier as ReservationQuerier
from internal.queries.seller import AsyncQuerier as SellerQuerier
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
        today = datetime.date.today()
        past_bundle_rows = [b for b in bundle_rows if b.bundle_date <= today]
        past_reservation_rows = [r for r in reservation_rows if r.bundle_date <= today]
        logger.debug(
            f"[Analytics] SalesVsPosted - seller_id={seller_id}, total_bundles={len(bundle_rows)}, "
            f"past_bundles={len(past_bundle_rows)}, total_reservations={len(reservation_rows)}, "
            f"past_reservations={len(past_reservation_rows)}, today={today}"
        )
        for i, point in enumerate(
            SellerAnalytics.graph_weekly_sales_vs_posted(
                past_bundle_rows, past_reservation_rows
            )
        ):
            logger.debug(
                f"[Analytics] SalesVsPosted point - date={point.day}, sold={point.sold_qty}, posted={point.posted_qty}"
            )
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
                logger.warning(
                    f"failed to get category {category.category_id}, skipping"
                )
                continue
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
        conn: AsyncConnection,
    ) -> None:
        """Add forecast vs posted graph for future bundles.

        Args:
            analytics_querier: async analytics queries
            seller_id: seller id
            bundle_rows: formatted bundle rows
            reservation_rows: formatted reservation rows
            conn: database connection for forecast querier
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

        forecast_querier = ForecastQuerier(conn)
        forecast_outputs = [
            row
            async for row in forecast_querier.get_forecast_outputs_by_seller(
                seller_id=seller_id
            )
        ]
        logger.debug(
            f"[Analytics] ForecastGraph - seller_id={seller_id}, total_forecasts_in_db={len(forecast_outputs)}"
        )

        today = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        future_forecasts = [
            f for f in forecast_outputs if f.window_start >= today_start
        ]
        logger.debug(
            f"[Analytics] ForecastGraph - today_start={today_start}, future_forecasts_count={len(future_forecasts)}"
        )

        if not future_forecasts:
            logger.warning(
                f"[Analytics] ForecastGraph - No future forecasts found for seller_id={seller_id}. "
                f"Run 'Refresh Analytics' to generate forecasts first."
            )
            return

        forecast_by_day: dict[datetime.date, tuple[int, int]] = {}
        forecast_count_by_day: dict[datetime.date, int] = {}
        for forecast in future_forecasts:
            logger.debug(
                f"[Analytics] ForecastGraph - bundle_id={forecast.bundle_id}, "
                f"window_start={forecast.window_start}, predicted_sales={forecast.predicted_sales}, "
                f"posted_qty={forecast.posted_qty}"
            )
            forecast_date = forecast.window_start.date()
            if forecast_date not in forecast_by_day:
                forecast_by_day[forecast_date] = (0, 0)
                forecast_count_by_day[forecast_date] = 0
            current = forecast_by_day[forecast_date]
            forecast_by_day[forecast_date] = (
                current[0] + forecast.predicted_sales,
                current[1] + forecast.posted_qty,
            )
            forecast_count_by_day[forecast_date] += 1

        avg_forecast_by_day = {
            date: (
                round(total_sales / forecast_count_by_day[date])
                if forecast_count_by_day[date] > 0
                else 0,
                round(total_posted / forecast_count_by_day[date])
                if forecast_count_by_day[date] > 0
                else 0,
            )
            for date, (total_sales, total_posted) in forecast_by_day.items()
        }
        logger.debug(
            f"[Analytics] ForecastGraph - aggregated by day (averaged): {avg_forecast_by_day}"
        )

        sorted_dates = sorted(avg_forecast_by_day.keys())
        for i, forecast_date in enumerate(sorted_dates):
            predicted_sales, posted_qty = avg_forecast_by_day[forecast_date]
            if (
                await analytics_querier.create_graph_point(
                    CreateGraphPointParams(
                        series_id=sales_series.series_id,
                        sort_index=i,
                        x=forecast_date.strftime("%Y-%m-%d"),
                        y=Decimal(predicted_sales),
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
                        x=forecast_date.strftime("%Y-%m-%d"),
                        y=Decimal(posted_qty),
                    )
                )
                is None
            ):
                logger.exception(
                    "failed to create point for posted series for forecast"
                )
                return

    @staticmethod
    async def add_forecast_outputs(
        forecast_querier: ForecastQuerier,
        category_querier: CategoryQuerier,
        seller_querier: SellerQuerier,
        seller_id: int,
        conn: AsyncConnection,
    ) -> None:
        """Save forecasts for seller's future bundles to forecast_output table."""
        logger.info(
            f"[Analytics] Starting forecast generation for seller_id={seller_id}"
        )
        history = [
            row
            async for row in forecast_querier.get_forecast_inputs_by_seller(
                seller_id=seller_id
            )
        ]
        logger.debug(
            f"[Analytics] ForecastOutputs - seller_id={seller_id}, history_rows={len(history)}"
        )

        seller = await seller_querier.get_seller(user_id=seller_id)
        if seller is None:
            logger.exception("failed to get seller for forecast")
            return

        bundles_querier = BundleQuerier(conn)
        bundles = [
            b async for b in bundles_querier.get_sellers_bundles(seller_id=seller_id)
        ]
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        future_bundles = [b for b in bundles if b.window_start > now]
        logger.debug(
            f"[Analytics] ForecastOutputs - total_bundles={len(bundles)}, "
            f"future_bundles={len(future_bundles)}, now={now}"
        )

        if not future_bundles:
            logger.warning(
                f"[Analytics] ForecastOutputs - No future bundles to forecast for seller_id={seller_id}"
            )
            return

        bundle_queries: list[tuple[int, ForecastQuery]] = []
        for bundle in future_bundles:
            categories = [
                cat_id
                async for cat_id in category_querier.get_bundle_categories(
                    bundle_id=bundle.bundle_id
                )
            ]
            details = BundleDetails(
                bundle_id=bundle.bundle_id,
                bundle_date=bundle.window_start.date(),
                window_start=bundle.window_start,
                window_end=bundle.window_end,
                seller_id=bundle.seller_id,
                category_ids=categories,
                latitude=seller.latitude,
                longitude=seller.longitude,
                posted_qty=bundle.total_qty,
            )
            query = build_forecast_query(details)
            bundle_queries.append((bundle.bundle_id, query))

        logger.info(
            f"[Analytics] Forecasting {len(bundle_queries)} bundles for seller_id={seller_id}"
        )
        forecasts = generate_seller_forecasts(history, bundle_queries)
        logger.info(
            f"[Analytics] Generated {len(forecasts)} forecasts, saving to database..."
        )

        for forecast in forecasts:
            logger.info(
                f"[Analytics] Forecast result - bundle_id={forecast.bundle_id}, "
                f"window_start={forecast.window_start}, predicted_sales={forecast.predicted_sales}, "
                f"confidence={forecast.confidence}"
            )
            await forecast_querier.upsert_forecast_output(
                UpsertForecastOutputParams(
                    bundle_id=forecast.bundle_id,
                    seller_id=forecast.seller_id,
                    window_start=forecast.window_start,
                    predicted_sales=forecast.predicted_sales,
                    posted_qty=forecast.posted_qty,
                    predicted_no_show_prob=forecast.predicted_no_show_prob,
                    confidence=forecast.confidence,
                    rationale=forecast.rationale,
                )
            )

    @staticmethod
    async def process_analytics(seller_id: int) -> None:
        """Background graph processing.

        Args:
            seller_id: seller_id

        """
        logger.info(
            f"[Analytics] ========== Starting analytics processing for seller_id={seller_id} =========="
        )
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
                    category_ids=list(reservation.category_ids)
                    if reservation.category_ids
                    else [],
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
            await AnalyticsProcesser.add_forecast_outputs(
                ForecastQuerier(conn),
                CategoryQuerier(conn),
                SellerQuerier(conn),
                seller_id,
                conn,
            )
            await AnalyticsProcesser.add_forecast_graph(
                analytics_querier, seller_id, bundle_rows, reservation_rows, conn
            )
            logger.info(
                f"[Analytics] ========== Completed analytics processing for seller_id={seller_id} =========="
            )
