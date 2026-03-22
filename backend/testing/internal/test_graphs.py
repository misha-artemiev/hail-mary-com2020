"""Tests for seller analytics graphs."""

from datetime import UTC, date, datetime, time
from unittest import TestCase

from internal.analytics.graphs import BundleRow, ReservationRow, SellerAnalytics


class TestGraphs(TestCase):
    """Test suite for SellerAnalytics graphing engine."""

    def test_graph_weekly_sales_vs_posted(self) -> None:  # noqa: PLR6301
        """Test chronological sorting and negative value clamping."""
        bundles = [
            BundleRow(bundle_date=date(2024, 1, 2), total_qty=10),
            BundleRow(bundle_date=date(2024, 1, 1), total_qty=-5),  # Should clamp to 0
        ]
        reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 2),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 2),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=None,  # No-show, shouldn't count
            ),
        ]

        result = SellerAnalytics.graph_weekly_sales_vs_posted(bundles, reservations)

        assert len(result) == 2  # noqa: PLR2004
        assert result[0].day == date(2024, 1, 1)
        assert result[1].day == date(2024, 1, 2)
        assert result[0].posted_qty == 0.0  # noqa: RUF069
        assert result[1].sold_qty == 1.0  # noqa: RUF069

    def test_graph_sell_through_rate_normal(self) -> None:  # noqa: PLR6301
        """Test accurate sell-through percentage calculation."""
        bundles = [BundleRow(bundle_date=date(2024, 1, 1), total_qty=10)]
        reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            )
            for _ in range(5)
        ]

        result = SellerAnalytics.graph_sell_through_rate(bundles, reservations)

        assert result.sell_through_percentage == 50.0  # noqa: PLR2004, RUF069

    def test_graph_sell_through_rate_zero_division(self) -> None:  # noqa: PLR6301
        """Test prevention of division by zero crashes."""
        result = SellerAnalytics.graph_sell_through_rate([], [])
        assert result.sell_through_percentage == 0.0  # noqa: RUF069

    def test_graph_sell_through_rate_capped(self) -> None:  # noqa: PLR6301
        """Test percentage capping to prevent over 100% glitches."""
        bundles = [BundleRow(bundle_date=date(2024, 1, 1), total_qty=5)]
        reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            )
            for _ in range(10)
        ]

        result = SellerAnalytics.graph_sell_through_rate(bundles, reservations)

        assert result.sell_through_percentage == 100.0  # noqa: PLR2004, RUF069

    def test_graph_category_distribution(self) -> None:  # noqa: PLR6301
        """Test grouping and sorting of category distributions."""
        reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[1, 2],  # Belongs to two categories
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[2],
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[3],
                collected_at=None,  # Should be ignored (no-show)
            ),
        ]

        result = SellerAnalytics.graph_category_distribution(reservations, top_n=2)

        assert len(result) == 2  # noqa: PLR2004
        assert result[0].category_id == 2  # noqa: PLR2004
        assert result[0].collected_qty == 2.0  # noqa: PLR2004, RUF069
        assert result[1].category_id == 1
        assert result[1].collected_qty == 1.0  # noqa: RUF069

    def test_graph_time_window_distribution(self) -> None:  # noqa: PLR6301
        """Test grouping and sorting of time window distributions."""
        reservations = [
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(10, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(9, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(10, 0),
                category_ids=[1],
                collected_at=datetime.now(tz=UTC),
            ),
            ReservationRow(
                bundle_date=date(2024, 1, 1),
                window_start=time(8, 0),
                category_ids=[1],
                collected_at=None,  # Should be ignored (no-show)
            ),
        ]

        result = SellerAnalytics.graph_time_window_distribution(reservations, top_n=2)

        assert len(result) == 2  # noqa: PLR2004
        assert result[0].time_window == time(10, 0)
        assert result[0].collected_qty == 2.0  # noqa: PLR2004, RUF069
        assert result[1].time_window == time(9, 0)
        assert result[1].collected_qty == 1.0  # noqa: RUF069
