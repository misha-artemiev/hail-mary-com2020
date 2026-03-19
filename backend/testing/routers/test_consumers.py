"""Tests for consumer endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import consumer_auth
from main import app
from testing.test_database import cleanup_database, init_database

TEST_RESERVATION_ID = 101
TEST_BUNDLE_ID = 5
TEST_USER_ID = 20


def override_consumer_auth() -> MagicMock:
    """Mock the consumer authentication dependency.

    Returns:
        MagicMock: Mock Object simualator.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    return mock


class TestConsumers(TestCase):
    """Test suite for consumer-related functionality."""

    def setUp(self) -> None:
        """Runs before every test to set up the client."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to tear down the client."""
        del self.client
        cleanup_database()

    @patch("routers.consumers.create_consumer")
    def test_register_consumer(self, mock_create: MagicMock) -> None:
        """Test consumer registration."""
        mock_create.return_value = True

        payload = {
            "username": "consumer_test",
            "email": "consumer@test.com",
            "password": "securepass",
            "first_name": "Furkan",
            "last_name": "RuggedHill",
        }

        response = self.client.post("/consumers", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        mock_create.assert_called_once()

    @patch("routers.consumers.ReservationsQuerier")
    def test_get_my_reservations(self, mock_querier: MagicMock) -> None:
        """Test getting logged-in user's reservations."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value

        mock_res = MagicMock()
        mock_res.reservation_id = TEST_RESERVATION_ID
        mock_res.bundle_id = TEST_BUNDLE_ID
        mock_res.claim_code = "ABC123XYZ"
        mock_res.status = "reserved"

        async def mock_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_res

        mock_instance.get_consumers_reservations.side_effect = mock_generator

        response = self.client.get("/consumers/me/reservations")

        # Debug print if it fails again to see validation errors
        if response.status_code != status.HTTP_200_OK:
            print(response.text)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["reservation_id"] == TEST_RESERVATION_ID

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ReservationsQuerier")
    def test_get_my_reservations_empty(self, mock_querier: MagicMock) -> None:
        """Test empty reservations returns empty list."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value

        async def mock_empty_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_instance.get_consumers_reservations.side_effect = mock_empty_generator

        response = self.client.get("/consumers/me/reservations")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_update_consumer(self, mock_querier: MagicMock) -> None:
        """Test updating consumer profile."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_instance.update_consumer = AsyncMock(return_value=True)

        payload = {"first_name": "Who", "last_name": "should it be"}

        response = self.client.patch("/consumers/me", json=payload)

        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_update_consumer_fail(self, mock_querier: MagicMock) -> None:
        """Test failure when updating consumer profile."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_instance.update_consumer = AsyncMock(return_value=None)

        payload = {"first_name": "X", "last_name": "Y"}

        response = self.client.patch("/consumers/me", json=payload)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_get_consumers(self, mock_querier: MagicMock) -> None:
        """Test getting all consumers."""
        mock_instance = mock_querier.return_value

        mock_consumer = MagicMock()
        mock_consumer.user_id = 1
        mock_consumer.username = "user"
        mock_consumer.email = "test@test.com"
        mock_consumer.fname = "First"
        mock_consumer.lname = "Last"

        async def mock_generator(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_consumer

        mock_instance.get_consumers.side_effect = mock_generator

        response = self.client.get("/consumers")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    @patch("routers.consumers.ConsumerQuerier")
    def test_get_consumer_me(self, mock_querier: MagicMock) -> None:
        """Test getting authenticated consumer profile."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_consumer = MagicMock()
        mock_consumer.user_id = TEST_USER_ID
        mock_consumer.username = "user"
        mock_consumer.email = "test@test.com"
        mock_consumer.fname = "First"
        mock_consumer.lname = "Last"
        mock_instance.get_consumer = AsyncMock(return_value=mock_consumer)

        response = self.client.get("/consumers/me")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["fname"] == "First"

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_get_consumer_by_id(self, mock_querier: MagicMock) -> None:
        """Test getting consumer by id."""
        mock_instance = mock_querier.return_value
        mock_consumer = MagicMock()
        mock_consumer.user_id = 1
        mock_consumer.username = "user"
        mock_consumer.email = "test@test.com"
        mock_consumer.fname = "First"
        mock_consumer.lname = "Last"
        mock_instance.get_consumer = AsyncMock(return_value=mock_consumer)

        response = self.client.get("/consumers/1")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["fname"] == "First"

    @patch("routers.consumers.BadgeQuerier")
    def test_get_consumer_badges(self, mock_querier: MagicMock) -> None:
        """Test getting consumer badges."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_instance = mock_querier.return_value

        mock_badge = MagicMock()
        mock_badge.badge_id = 1
        mock_badge.level = 1
        mock_badge.name = "Badge"
        mock_badge.description = "Desc"

        async def mock_generator(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_badge

        mock_instance.get_consumer_badges.side_effect = mock_generator

        response = self.client.get("/consumers/me/badges")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ReservationsQuerier")
    def test_get_streaks(self, mock_querier: MagicMock) -> None:
        """Test getting consumer streaks."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_instance = mock_querier.return_value

        async def mock_empty_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_instance.get_consumers_reservations_full.side_effect = mock_empty_gen

        response = self.client.get("/consumers/me/streaks")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == 0

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.SellerIssueReportsQuerier")
    @patch("routers.consumers.ReservationsQuerier")
    def test_create_seller_issue_report(
        self, mock_res_q: MagicMock, mock_rep_q: MagicMock
    ) -> None:
        """Test creating a seller issue report."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_res_instance = mock_res_q.return_value
        mock_res = MagicMock()
        mock_res.consumer_id = TEST_USER_ID
        mock_res_instance.get_reservation = AsyncMock(return_value=mock_res)

        mock_rep_instance = mock_rep_q.return_value
        mock_report = MagicMock()
        mock_report.report_id = 1
        mock_report.reservation_id = 1
        mock_report.issue_type = "ITEM_MISSING"
        mock_report.description = "Bad"
        mock_report.status = "open"
        mock_rep_instance.create_seller_issue_report = AsyncMock(
            return_value=mock_report
        )

        payload = {"issue_type": "ITEM_MISSING", "description": "Bad"}

        response = self.client.post("/consumers/me/reservations/1/report", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["issue_type"] == "ITEM_MISSING"

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.AdminIssueReportsQuerier")
    def test_create_admin_issue_report(self, mock_querier: MagicMock) -> None:
        """Test creating an admin issue report."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_report = MagicMock()
        mock_report.report_id = 1
        mock_report.user_id = TEST_USER_ID
        mock_report.issue_type = "APP_CRASH"
        mock_report.description = "Bug"
        mock_report.status = "open"
        mock_instance.create_admin_issue_report = AsyncMock(return_value=mock_report)

        payload = {"issue_type": "APP_CRASH", "description": "Bug"}

        response = self.client.post("/consumers/me/reports/admin", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["issue_type"] == "APP_CRASH"

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.AdminIssueReportsQuerier")
    def test_get_admin_issue_reports(self, mock_querier: MagicMock) -> None:
        """Test getting admin issue reports."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_report = MagicMock()
        mock_report.report_id = 1
        mock_report.user_id = TEST_USER_ID
        mock_report.issue_type = "APP_CRASH"
        mock_report.description = "Bug"
        mock_report.status = "open"

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_report

        mock_instance.get_admin_issue_reports_by_user.side_effect = mock_gen

        response = self.client.get("/consumers/me/reports/admin")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.SellerIssueReportsQuerier")
    def test_get_seller_issue_reports(self, mock_querier: MagicMock) -> None:
        """Test getting seller issue reports."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_instance = mock_querier.return_value
        mock_report = MagicMock()
        mock_report.report_id = 1
        mock_report.reservation_id = 1
        mock_report.issue_type = "ITEM_MISSING"
        mock_report.description = "Bad"
        mock_report.status = "open"

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_report

        mock_instance.get_seller_issue_reports_by_user.side_effect = mock_gen

        response = self.client.get("/consumers/me/reports/seller")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

        del app.dependency_overrides[consumer_auth]
