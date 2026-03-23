"""Badges processing engine."""

from datetime import UTC, datetime, timedelta

from fastapi import BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncConnection

from internal.database.manager import database_manager
from internal.queries.badge import (
    AcquireBadgeParams,
    GetConsumerBadgesRow,
    UpdateBadgeLevelParams,
)
from internal.queries.badge import AsyncQuerier as BadgeQuerier
from internal.queries.models import BadgesAcquired
from internal.queries.reservations import AsyncQuerier as ReservationQuerier
from internal.queries.reservations import GetConsumersReservationsFullRow
from internal.settings.config import BadgesConfig, badges_config


class BadgeEngine:
    """Badges acquiring engine."""

    background_tasks: BackgroundTasks

    class AcquireBadgeRule(BaseModel):
        """Next badge level to acquire."""

        badge_id: int
        rule: BadgesConfig.BadgeGoal

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        """Init engine for consumer."""
        self.background_tasks = background_tasks

    def run(self, consumer_id: int, bundle_window_start: datetime) -> None:
        """Starts background badge check task.

        Args:
            consumer_id: consumer id
            bundle_window_start: current collection window start
        """
        badges_rules = badges_config.badges_rules.badges_rules
        self.background_tasks.add_task(
            self.process_badges, consumer_id, badges_rules, bundle_window_start
        )

    @staticmethod
    def to_acquire(
        badges_rules: list[BadgesConfig.BadgeRules],
        acquired_badges: list[GetConsumerBadgesRow],
    ) -> list[BadgeEngine.AcquireBadgeRule]:
        """Gives levels of badges next to be acquired.

        Args:
            badges_rules: all rules for all badges
            acquired_badges: badges acquired by consumer

        Returns:
            list of badges levels to acquire next
        """
        acquired_levels = {badge.badge_id: badge.level for badge in acquired_badges}
        to_acquire_badges: list[BadgeEngine.AcquireBadgeRule] = []
        for badge_rules in badges_rules:
            current_level = acquired_levels.get(badge_rules.badge_id, 0)
            next_level_rule = next(
                (rule for rule in badge_rules.rules if rule.level > current_level), None
            )
            if not next_level_rule:
                continue
            to_acquire_badges.append(
                BadgeEngine.AcquireBadgeRule(
                    badge_id=badge_rules.badge_id, rule=next_level_rule
                )
            )
        return to_acquire_badges

    @staticmethod
    def quantity_goal(
        reservations_full: list[GetConsumersReservationsFullRow],
        rule: BadgesConfig.QuantityGoal,
    ) -> bool:
        """Quantity goal rule check.

        Args:
            reservations_full: extended reservations info,
            rule: rules for this badge

        Returns:
            if badge meets requirements
        """
        reservations_filtered = [
            reservation
            for reservation in reservations_full
            if reservation.collected_at is not None
        ]
        if rule.category_id:
            reservations_filtered = [
                reservation
                for reservation in reservations_filtered
                if reservation.category_ids
                and rule.category_id in reservation.category_ids
            ]
        if rule.seller_id:
            reservations_filtered = [
                reservation
                for reservation in reservations_filtered
                if reservation.seller_id == rule.seller_id
            ]
        return not len(reservations_filtered) < rule.quantity

    @staticmethod
    def co2_goal(
        reservations_full: list[GetConsumersReservationsFullRow],
        rule: BadgesConfig.CO2Goal,
    ) -> bool:
        """CO2 goal rule check.

        Args:
            reservations_full: extended reservations info,
            rule: rules for this badge

        Returns:
            if badge meets requirements
        """
        reservations_filtered = [
            reservation
            for reservation in reservations_full
            if reservation.collected_at is not None
        ]
        carbon_dioxide = sum(
            reservation.carbon_dioxide for reservation in reservations_filtered
        )
        return not carbon_dioxide < rule.carbon_dioxide

    @staticmethod
    def diversity_goal(
        reservations_full: list[GetConsumersReservationsFullRow],
        rule: BadgesConfig.DiversityGoal,
    ) -> bool:
        """Diversity goal rule check.

        Args:
            reservations_full: extended reservations info,
            rule: rules for this badge

        Returns:
            if badge meets requirements
        """
        reservations_filtered = [
            reservation
            for reservation in reservations_full
            if reservation.collected_at is not None
        ]
        if rule.dif_categories >= 1:
            categories = {
                cid
                for reservation in reservations_filtered
                if reservation.category_ids
                for cid in reservation.category_ids
            }
            if len(categories) < rule.dif_categories:
                return False
        if rule.dif_sellers >= 1:
            sellers = {reservation.seller_id for reservation in reservations_filtered}
            if len(sellers) < rule.dif_sellers:
                return False
        return True

    @staticmethod
    def streak_goal_filter_sort(
        reservations_full: list[GetConsumersReservationsFullRow],
        rule: BadgesConfig.StreakGoal,
    ) -> list[GetConsumersReservationsFullRow]:
        """Filter and sort reservations for streak goal.

        Args:
            reservations_full: reservations with extended info
            rule: badge rules

        Returns:
            list of sorted and filtered reservations
        """
        reservations_filtered = reservations_full.copy()
        if rule.category_id:
            reservations_filtered = [
                reservation
                for reservation in reservations_filtered
                if reservation.category_ids
                and rule.category_id in reservation.category_ids
            ]
        if rule.seller_id:
            reservations_filtered = [
                reservation
                for reservation in reservations_filtered
                if reservation.seller_id == rule.seller_id
            ]
        return sorted(
            reservations_filtered,
            key=lambda reservation: reservation.window_start,
            reverse=True,
        )

    @staticmethod
    def streak_goal(
        reservations_full: list[GetConsumersReservationsFullRow],
        rule: BadgesConfig.StreakGoal,
        bundle_window_start: datetime,
    ) -> bool:
        """Streak goal rule check.

        Args:
            reservations_full: extended reservations info,
            rule: rules for this badge
            bundle_window_start: window start for current collection

        Returns:
            if badge meets requirements
        """
        reservations_sorted = BadgeEngine.streak_goal_filter_sort(
            reservations_full, rule
        )
        reservations_streak: list[GetConsumersReservationsFullRow] = []
        for reservation in reservations_sorted:
            if (
                not reservation.collected_at is not None
                and reservation.window_end > datetime.now(tz=UTC)
            ):
                continue
            if not reservation.collected_at:
                break
            reservations_streak.append(reservation)
        if (
            rule.streak_quantity >= 1
            and len(reservations_streak) < rule.streak_quantity
        ):
            return False
        if rule.streak_days >= 1:
            days = 0
            previous_date = bundle_window_start.date() + timedelta(days=1)
            for reservation in reservations_streak:
                reservation_date = reservation.window_start.date()
                if reservation_date + timedelta(days=1) == previous_date:
                    days += 1
                    previous_date = reservation_date
                    continue
                if reservation_date != previous_date:
                    break
            if days < rule.streak_days:
                return False
        return True

    @staticmethod
    async def update_badge(
        conn: AsyncConnection, consumer_id: int, badge_id: int, level: int
    ) -> BadgesAcquired | None:
        """Inserts or updates acquired badge record.

        Args:
            conn: database connection
            consumer_id: consumer id
            badge_id: badge id
            level: badge level

        Returns:
            acquired badge
        """
        if level == 1:
            return await BadgeQuerier(conn).acquire_badge(
                AcquireBadgeParams(user_id=consumer_id, badge_id=badge_id, level=level)
            )
        return await BadgeQuerier(conn).update_badge_level(
            UpdateBadgeLevelParams(user_id=consumer_id, badge_id=badge_id, level=level)
        )

    @staticmethod
    async def process_badges(
        consumer_id: int,
        badges_rules: list[BadgesConfig.BadgeRules],
        bundle_window_start: datetime,
    ) -> None:
        """Background task to acquire badges.

        Args:
            consumer_id: consumer id
            badges_rules: rules for all badges
            bundle_window_start: start window for current collection

        Raises:
            ValueError: if failed to acquire badge
        """
        async for conn in database_manager.get_connection():
            badges = [
                badges
                async for badges in BadgeQuerier(conn).get_consumer_badges(
                    user_id=consumer_id
                )
            ]
            if not (acquire_badges := BadgeEngine.to_acquire(badges_rules, badges)):
                return
            reservations_full = [
                reservation
                async for reservation in ReservationQuerier(
                    conn
                ).get_consumers_reservations_full(consumer_id=consumer_id)
            ]
            for acquire_badge in acquire_badges:
                rule = acquire_badge.rule
                to_acquire = False
                match rule:
                    case BadgesConfig.QuantityGoal():
                        to_acquire = BadgeEngine.quantity_goal(reservations_full, rule)
                    case BadgesConfig.CO2Goal():
                        to_acquire = BadgeEngine.co2_goal(reservations_full, rule)
                    case BadgesConfig.DiversityGoal():
                        to_acquire = BadgeEngine.diversity_goal(reservations_full, rule)
                    case BadgesConfig.StreakGoal():
                        to_acquire = BadgeEngine.streak_goal(
                            reservations_full, rule, bundle_window_start
                        )
                if not to_acquire:
                    continue
                acquired_badge = await BadgeEngine.update_badge(
                    conn, consumer_id, acquire_badge.badge_id, acquire_badge.rule.level
                )
                if not acquired_badge:
                    raise ValueError("Failed to insert acquire badge record")
