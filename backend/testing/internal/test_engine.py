"""Tests for badges processing engine."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import BackgroundTasks
from internal.badges.engine import BadgeEngine
from internal.queries.reservations import GetConsumersReservationsFullRow
from internal.settings.config import BadgesConfig

# Constants
TEST_QTY = 5
TEST_CO2 = 100.0


class FakeRes:
    """Fake reservation object to bypass MagicMock hashing quirks."""

    def __init__(self, cat_id: int, sel_id: int) -> None:
        """Init with required values."""
        self.collected_at = datetime.now(tz=UTC)
        self.window_start = datetime.now(tz=UTC)
        self.window_end = datetime.now(tz=UTC)
        self.category_id = cat_id
        self.category_ids = [cat_id]
        self.seller_id = sel_id
        self.carbon_dioxide = TEST_CO2


class TestBadgeEngine(IsolatedAsyncioTestCase):
    """Test suite for the BadgeEngine rules and background runner."""

    def setUp(self) -> None:
        """Initialize mock data used across badge tests."""
        self.mock_res_collected = FakeRes(1, 1)

    def test_quantity_goal_success(self) -> None:
        """Test that the quantity goal returns true when met."""
        rule = BadgesConfig.QuantityGoal(
            type="quantity", level=1, quantity=1, category_id=None, seller_id=None
        )
        reservations = cast(
            list[GetConsumersReservationsFullRow], [self.mock_res_collected]
        )

        result = BadgeEngine.quantity_goal(reservations, rule)
        assert result is True

    def test_quantity_goal_failure(self) -> None:
        """Test that the quantity goal returns false when not met."""
        rule = BadgesConfig.QuantityGoal(
            type="quantity",
            level=1,
            quantity=TEST_QTY,
            category_id=None,
            seller_id=None,
        )
        reservations = cast(
            list[GetConsumersReservationsFullRow], [self.mock_res_collected]
        )

        result = BadgeEngine.quantity_goal(reservations, rule)
        assert result is False

    def test_co2_goal_success(self) -> None:
        """Test that the CO2 goal evaluates correctly."""
        rule = BadgesConfig.CO2Goal(type="co2", level=1, carbon_dioxide=TEST_CO2)
        reservations = cast(
            list[GetConsumersReservationsFullRow], [self.mock_res_collected]
        )

        result = BadgeEngine.co2_goal(reservations, rule)
        assert result is True

    def test_co2_goal_failure(self) -> None:
        """Test that the CO2 goal evaluates false when requirement is not met."""
        rule = BadgesConfig.CO2Goal(type="co2", level=1, carbon_dioxide=200.0)
        reservations = cast(
            list[GetConsumersReservationsFullRow], [self.mock_res_collected]
        )

        result = BadgeEngine.co2_goal(reservations, rule)
        assert result is False

    def test_diversity_goal_success(self) -> None:  # noqa: PLR6301
        """Test diversity goal over categories and sellers."""
        mock_res_1 = FakeRes(cat_id=1, sel_id=1)
        mock_res_2 = FakeRes(cat_id=2, sel_id=2)

        rule = BadgesConfig.DiversityGoal(
            type="diversity", level=1, dif_categories=2, dif_sellers=0
        )
        reservations = cast(
            list[GetConsumersReservationsFullRow], [mock_res_1, mock_res_2]
        )

        result = BadgeEngine.diversity_goal(reservations, rule)
        assert result is True

    def test_diversity_goal_failure(self) -> None:  # noqa: PLR6301
        """Test diversity goal failure when variety targets are not met."""
        mock_res_1 = FakeRes(cat_id=1, sel_id=1)
        mock_res_2 = FakeRes(cat_id=1, sel_id=1)

        rule = BadgesConfig.DiversityGoal(
            type="diversity", level=1, dif_categories=2, dif_sellers=0
        )
        reservations = cast(
            list[GetConsumersReservationsFullRow], [mock_res_1, mock_res_2]
        )

        result = BadgeEngine.diversity_goal(reservations, rule)
        assert result is False

    def test_streak_goal_success(self) -> None:  # noqa: PLR6301
        """Test calculating consecutive daily streaks."""
        window_start = datetime.now(tz=UTC)

        mock_res_today = FakeRes(1, 1)
        mock_res_today.collected_at = window_start
        mock_res_today.window_start = window_start
        mock_res_today.window_end = window_start

        rule = BadgesConfig.StreakGoal(
            type="streak",
            level=1,
            streak_days=1,
            streak_quantity=0,
            category_id=None,
            seller_id=None,
        )

        reservations = cast(list[GetConsumersReservationsFullRow], [mock_res_today])

        result = BadgeEngine.streak_goal(reservations, rule, window_start)
        assert result is True

    def test_streak_goal_failure(self) -> None:  # noqa: PLR6301
        """Test calculating consecutive daily streaks failure."""
        window_start = datetime.now(tz=UTC)

        mock_res_today = FakeRes(1, 1)
        mock_res_today.collected_at = window_start
        mock_res_today.window_start = window_start
        mock_res_today.window_end = window_start

        rule = BadgesConfig.StreakGoal(
            type="streak",
            level=1,
            streak_days=2,
            streak_quantity=0,
            category_id=None,
            seller_id=None,
        )

        reservations = cast(list[GetConsumersReservationsFullRow], [mock_res_today])

        result = BadgeEngine.streak_goal(reservations, rule, window_start)
        assert result is False

    @patch("internal.badges.engine.badges_config")
    def test_run_background_task(self, mock_badges_config: MagicMock) -> None:  # noqa: PLR6301
        """Test the engine successfully schedules the background job."""
        mock_bg_tasks = MagicMock(spec=BackgroundTasks)
        engine = BadgeEngine(mock_bg_tasks)

        mock_badges_config.badges_rules = MagicMock()
        mock_badges_config.badges_rules.badges_rules = []

        engine.run(consumer_id=1, bundle_window_start=datetime.now(tz=UTC))

        mock_bg_tasks.add_task.assert_called_once()
        assert mock_bg_tasks.add_task.call_args[0][0] == engine.process_badges

    def test_to_acquire_logic(self) -> None:  # noqa: PLR6301
        """Test logic that maps acquired badges to their next available tier."""
        mock_rule_lvl1 = BadgesConfig.QuantityGoal(
            type="quantity", level=1, quantity=1, category_id=None, seller_id=None
        )
        mock_rule_lvl2 = BadgesConfig.QuantityGoal(
            type="quantity", level=2, quantity=5, category_id=None, seller_id=None
        )
        mock_badge_def = MagicMock()
        mock_badge_def.badge_id = 99
        mock_badge_def.rules = [mock_rule_lvl1, mock_rule_lvl2]

        mock_acquired = MagicMock()
        mock_acquired.badge_id = 99
        mock_acquired.level = 1

        to_acquire = BadgeEngine.to_acquire([mock_badge_def], [mock_acquired])

        assert len(to_acquire) == 1
        assert to_acquire[0].badge_id == 99  # noqa: PLR2004
        assert to_acquire[0].rule == mock_rule_lvl2

    @patch("internal.badges.engine.BadgeQuerier")
    async def test_update_badge_level_1(self, mock_querier: MagicMock) -> None:  # noqa: PLR6301
        """Test inserting a brand new level 1 badge."""
        mock_conn = MagicMock()
        mock_instance = mock_querier.return_value
        mock_instance.acquire_badge = AsyncMock(return_value=MagicMock())

        result = await BadgeEngine.update_badge(mock_conn, 1, 99, 1)

        assert result is not None
        mock_instance.acquire_badge.assert_called_once()
        mock_instance.update_badge_level.assert_not_called()

    @patch("internal.badges.engine.BadgeQuerier")
    async def test_update_badge_level_2(self, mock_querier: MagicMock) -> None:  # noqa: PLR6301
        """Test updating an existing badge to a higher level."""
        mock_conn = MagicMock()
        mock_instance = mock_querier.return_value
        mock_instance.update_badge_level = AsyncMock(return_value=MagicMock())

        result = await BadgeEngine.update_badge(mock_conn, 1, 99, 2)

        assert result is not None
        mock_instance.update_badge_level.assert_called_once()
        mock_instance.acquire_badge.assert_not_called()

    @patch("internal.badges.engine.database_manager")
    @patch("internal.badges.engine.BadgeQuerier")
    @patch("internal.badges.engine.ReservationQuerier")
    @patch.object(BadgeEngine, "to_acquire")
    @patch.object(BadgeEngine, "quantity_goal")
    @patch.object(BadgeEngine, "update_badge")
    async def test_process_badges_success(  # noqa: PLR0913, PLR0917, PLR6301
        self,
        mock_update_badge: MagicMock,
        mock_q_goal: MagicMock,
        mock_to_acquire: MagicMock,
        mock_res_q: MagicMock,
        mock_badge_q: MagicMock,
        mock_db_manager: MagicMock,
    ) -> None:
        """Test full background loop processing a badge acquisition."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield MagicMock()

        async def mock_empty_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_db_manager.get_connection.side_effect = mock_conn_gen
        mock_badge_q.return_value.get_consumer_badges.side_effect = mock_empty_gen
        mock_res_q.return_value.get_consumers_reservations_full.side_effect = (
            mock_empty_gen
        )

        mock_rule = BadgesConfig.QuantityGoal(
            type="quantity", level=1, quantity=1, category_id=None, seller_id=None
        )
        mock_to_acquire.return_value = [
            BadgeEngine.AcquireBadgeRule(badge_id=99, rule=mock_rule)
        ]
        mock_q_goal.return_value = True

        async def dummy_update(*args: Any, **kwargs: Any) -> MagicMock:  # noqa: ANN401, RUF029
            return MagicMock()

        mock_update_badge.side_effect = dummy_update

        await BadgeEngine.process_badges(
            consumer_id=1, badges_rules=[], bundle_window_start=datetime.now(tz=UTC)
        )

        mock_update_badge.assert_called_once()

    @patch("internal.badges.engine.database_manager")
    @patch("internal.badges.engine.BadgeQuerier")
    @patch("internal.badges.engine.ReservationQuerier")
    @patch.object(BadgeEngine, "to_acquire")
    @patch.object(BadgeEngine, "quantity_goal")
    @patch.object(BadgeEngine, "update_badge")
    async def test_process_badges_failure(  # noqa: PLR0913, PLR0917
        self,
        mock_update_badge: MagicMock,
        mock_q_goal: MagicMock,
        mock_to_acquire: MagicMock,
        mock_res_q: MagicMock,
        mock_badge_q: MagicMock,
        mock_db_manager: MagicMock,
    ) -> None:
        """Test ValueError is raised if database insert fails."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield MagicMock()

        async def mock_empty_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_db_manager.get_connection.side_effect = mock_conn_gen
        mock_badge_q.return_value.get_consumer_badges.side_effect = mock_empty_gen
        mock_res_q.return_value.get_consumers_reservations_full.side_effect = (
            mock_empty_gen
        )

        mock_rule = BadgesConfig.QuantityGoal(
            type="quantity", level=1, quantity=1, category_id=None, seller_id=None
        )
        mock_to_acquire.return_value = [
            BadgeEngine.AcquireBadgeRule(badge_id=99, rule=mock_rule)
        ]
        mock_q_goal.return_value = True

        async def dummy_update_fail(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401, RUF029
            return None

        mock_update_badge.side_effect = dummy_update_fail

        with self.assertRaises(ValueError) as context:
            await BadgeEngine.process_badges(
                consumer_id=1, badges_rules=[], bundle_window_start=datetime.now(tz=UTC)
            )

        assert "Failed to insert" in str(context.exception)
