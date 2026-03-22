"""Tests for graph refreshing background processing."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, time
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import BackgroundTasks
from internal.analytics.graphs import BundleRow, ReservationRow
from internal.analytics.processing import AnalyticsProcesser


class TestProcessing(IsolatedAsyncioTestCase):
    """Test suite for the AnalyticsProcesser background jobs."""

    def setUp(self) -> None:
        """Initialize reusable mock rows for the graphs."""
        self.bundles = [BundleRow(bundle_date=date(2024, 1, 1), total_qty=10)]
        self.reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            )
        ]

    def test_run_background_task(self) -> None:  # noqa: PLR6301
        """Test the processor successfully schedules the background job."""
        mock_bg_tasks = MagicMock(spec=BackgroundTasks)
        processor = AnalyticsProcesser(mock_bg_tasks)

        processor.run(seller_id=1)

        mock_bg_tasks.add_task.assert_called_once()
        assert mock_bg_tasks.add_task.call_args[0][0] == processor.process_analytics

    async def test_add_sales_vs_posted_graph(self) -> None:
        """Test compiling and saving the sales vs posted graph points."""
        mock_querier = MagicMock()
        mock_graph = MagicMock()
        mock_graph.graph_id = 1
        mock_querier.get_graph = AsyncMock(return_value=mock_graph)

        mock_series = MagicMock()
        mock_series.series_id = 10
        mock_querier.create_graph_series = AsyncMock(return_value=mock_series)
        mock_querier.create_graph_point = AsyncMock(return_value=MagicMock())

        await AnalyticsProcesser.add_sales_vs_posted_graph(
            mock_querier, 1, self.bundles, self.reservations
        )

        assert mock_querier.create_graph_series.call_count == 2  # noqa: PLR2004
        assert mock_querier.create_graph_point.call_count == 2  # noqa: PLR2004

    async def test_add_sell_through_rate_graph(self) -> None:
        """Test compiling and saving the sell-through rate gauge."""
        mock_querier = MagicMock()
        mock_graph = MagicMock()
        mock_graph.graph_id = 2
        mock_querier.get_graph = AsyncMock(return_value=mock_graph)

        mock_series = MagicMock()
        mock_series.series_id = 20
        mock_querier.create_graph_series = AsyncMock(return_value=mock_series)
        mock_querier.create_graph_point = AsyncMock(return_value=MagicMock())

        await AnalyticsProcesser.add_sell_through_rate_graph(
            mock_querier, 1, self.bundles, self.reservations
        )

        mock_querier.create_graph_series.assert_called_once()
        assert mock_querier.create_graph_point.call_count == 2  # noqa: PLR2004

    @patch("internal.analytics.processing.CategoryQuerier")
    async def test_add_cateogry_distribution_graph(self, mock_cat_q: MagicMock) -> None:
        """Test compiling and saving the category distribution."""
        mock_querier = MagicMock()
        mock_graph = MagicMock()
        mock_graph.graph_id = 3
        mock_querier.get_graph = AsyncMock(return_value=mock_graph)

        mock_series = MagicMock()
        mock_series.series_id = 30
        mock_querier.create_graph_series = AsyncMock(return_value=mock_series)
        mock_querier.create_graph_point = AsyncMock(return_value=MagicMock())

        mock_cat_instance = mock_cat_q.return_value
        mock_cat = MagicMock()
        mock_cat.category_name = "Test Category"
        mock_cat_instance.get_category = AsyncMock(return_value=mock_cat)

        await AnalyticsProcesser.add_cateogry_distribution_graph(
            mock_querier, 1, self.reservations, MagicMock()
        )

        mock_querier.create_graph_series.assert_called_once()
        mock_querier.create_graph_point.assert_called_once()

    async def test_add_time_window_distribution_graph(self) -> None:
        """Test compiling and saving the time window distribution."""
        mock_querier = MagicMock()
        mock_graph = MagicMock()
        mock_graph.graph_id = 4
        mock_querier.get_graph = AsyncMock(return_value=mock_graph)

        mock_series = MagicMock()
        mock_series.series_id = 40
        mock_querier.create_graph_series = AsyncMock(return_value=mock_series)
        mock_querier.create_graph_point = AsyncMock(return_value=MagicMock())

        await AnalyticsProcesser.add_time_window_distribution_graph(
            mock_querier, 1, self.reservations
        )

        mock_querier.create_graph_series.assert_called_once()
        mock_querier.create_graph_point.assert_called_once()

    @patch("internal.analytics.processing.database_manager")
    @patch("internal.analytics.processing.AnalyticsQuerier")
    @patch("internal.analytics.processing.BundleQuerier")
    @patch("internal.analytics.processing.ReservationQuerier")
    @patch.object(AnalyticsProcesser, "add_sales_vs_posted_graph")
    @patch.object(AnalyticsProcesser, "add_sell_through_rate_graph")
    @patch.object(AnalyticsProcesser, "add_cateogry_distribution_graph")
    @patch.object(AnalyticsProcesser, "add_time_window_distribution_graph")
    async def test_process_analytics_success(  # noqa: PLR0913, PLR0917, PLR6301
        self,
        mock_time_win: MagicMock,
        mock_cat_dist: MagicMock,
        mock_sell_rate: MagicMock,
        mock_sales_vs: MagicMock,
        mock_res_q: MagicMock,
        mock_bundle_q: MagicMock,
        mock_analytics_q: MagicMock,
        mock_db_manager: MagicMock,
    ) -> None:
        """Test the master process_analytics loop triggers all sub-graphs."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield MagicMock()

        async def mock_empty_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_db_manager.get_connection.side_effect = mock_conn_gen

        # Setup Analytics Querier
        mock_aq_inst = mock_analytics_q.return_value
        mock_aq_inst.get_graphs_types.side_effect = mock_empty_gen

        # Setup Bundle Querier
        mock_bq_inst = mock_bundle_q.return_value
        mock_bq_inst.get_sellers_bundles.side_effect = mock_empty_gen

        # Setup Reservation Querier
        mock_rq_inst = mock_res_q.return_value
        mock_rq_inst.get_seller_reservations_full.side_effect = mock_empty_gen

        mock_sales_vs.return_value = None
        mock_sell_rate.return_value = None
        mock_cat_dist.return_value = None
        mock_time_win.return_value = None

        await AnalyticsProcesser.process_analytics(seller_id=1)

        mock_sales_vs.assert_called_once()
        mock_sell_rate.assert_called_once()
        mock_cat_dist.assert_called_once()
        mock_time_win.assert_called_once()
