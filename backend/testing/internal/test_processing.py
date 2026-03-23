"""Tests for graph refreshing background processing."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, time
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

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

    @patch.object(AnalyticsProcesser, "add_forecast_outputs")
    @patch.object(AnalyticsProcesser, "add_forecast_graph")
    @patch.object(AnalyticsProcesser, "add_time_window_distribution_graph")
    @patch.object(AnalyticsProcesser, "add_cateogry_distribution_graph")
    @patch.object(AnalyticsProcesser, "add_sell_through_rate_graph")
    @patch.object(AnalyticsProcesser, "add_sales_vs_posted_graph")
    @patch("internal.analytics.processing.ReservationQuerier")
    @patch("internal.analytics.processing.BundleQuerier")
    @patch("internal.analytics.processing.AnalyticsQuerier")
    @patch("internal.analytics.processing.database_manager")
    async def test_process_analytics_success(  # noqa: PLR0913, PLR0917, PLR6301
        self,
        mock_db_manager: MagicMock,
        mock_analytics_q: MagicMock,
        mock_bundle_q: MagicMock,
        mock_res_q: MagicMock,
        mock_sales_vs: MagicMock,
        mock_sell_rate: MagicMock,
        mock_cat_dist: MagicMock,
        mock_time_win: MagicMock,
        mock_f_graph: MagicMock,
        mock_f_outputs: MagicMock,
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

        # Use async dummy functions to avoid await TypeErrors
        async def dummy_func(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401, RUF029
            return None

        mock_sales_vs.side_effect = dummy_func
        mock_sell_rate.side_effect = dummy_func
        mock_cat_dist.side_effect = dummy_func
        mock_time_win.side_effect = dummy_func
        mock_f_graph.side_effect = dummy_func
        mock_f_outputs.side_effect = dummy_func

        await AnalyticsProcesser.process_analytics(seller_id=1)

        mock_sales_vs.assert_called_once()
        mock_sell_rate.assert_called_once()
        mock_cat_dist.assert_called_once()
        mock_time_win.assert_called_once()
        mock_f_graph.assert_called_once()
        mock_f_outputs.assert_called_once()
