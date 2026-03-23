"""Tests for consumer endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
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


class MockModel:
    """Mock models for consumer validation."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: D107, ANN401
        self.user_id = TEST_USER_ID
        self.username = "test"
        self.email = "test@test.com"
        self.fname = "A"
        self.lname = "B"
        self.role = "consumer"
        self.created_at = datetime.now(tz=UTC)
        self.last_login = datetime.now(tz=UTC)
        self.acquired_at = datetime.now(tz=UTC)
        self.bundle_name = "Bundle"
        self.seller_name = "Seller"
        self.description = "Desc"
        self.price = 10.0
        self.discount_percentage = 50
        self.total_qty = 5
        self.__dict__.update(kwargs)


def override_consumer_auth() -> MagicMock:
    """Mock consumer auth.

    Returns:
        MagicMock: Mock object with user_id.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    return mock


class TestConsumers(TestCase):
    """Test suite."""

    def setUp(self) -> None:  # noqa: D102
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:  # noqa: D102
        del self.client
        cleanup_database()

    @patch("routers.consumers.create_consumer", new_callable=AsyncMock)
    def test_register_consumer(self, mock_create: AsyncMock) -> None:
        """Test registration."""
        mock_create.return_value = MockModel()
        payload = {
            "username": "u",
            "email": "e@e.com",
            "password": "p",
            "first_name": "f",
            "last_name": "l",
        }
        response = self.client.post("/consumers", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

    @patch("routers.consumers.create_consumer", new_callable=AsyncMock)
    def test_register_consumer_fail(self, mock_create: AsyncMock) -> None:
        """Test registration fail."""
        mock_create.side_effect = ValueError("err")
        payload = {
            "username": "u",
            "email": "e@e.com",
            "password": "p",
            "first_name": "f",
            "last_name": "l",
        }
        response = self.client.post("/consumers", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("routers.consumers.ConsumerQuerier")
    def test_get_consumer(self, mock_querier: MagicMock) -> None:
        """Test get specific consumer."""
        mock_querier.return_value.get_consumer = AsyncMock(return_value=MockModel())
        response = self.client.get(f"/consumers/{TEST_USER_ID}")
        assert response.status_code == status.HTTP_200_OK

    @patch("routers.consumers.ConsumerQuerier")
    def test_get_consumer_me(self, mock_querier: MagicMock) -> None:
        """Test get me."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_querier.return_value.get_consumer = AsyncMock(return_value=MockModel())
        response = self.client.get("/consumers/me")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_update_consumer(self, mock_querier: MagicMock) -> None:
        """Test update me."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_updated = MockModel(fname="New")
        mock_querier.return_value.update_consumer = AsyncMock(return_value=mock_updated)
        response = self.client.patch(
            "/consumers/me", json={"first_name": "New", "last_name": "B"}
        )
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    def test_update_consumer_fail(self, mock_querier: MagicMock) -> None:
        """Test update fail."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_querier.return_value.update_consumer = AsyncMock(return_value=None)
        response = self.client.patch(
            "/consumers/me", json={"first_name": "N", "last_name": "S"}
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ReservationsQuerier")
    def test_get_consumer_reservations(self, mock_querier: MagicMock) -> None:
        """Test get reservations."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_res = MockModel(
            reservation_id=TEST_RESERVATION_ID,
            bundle_id=TEST_BUNDLE_ID,
            window_start=datetime.now(tz=UTC),
            window_end=datetime.now(tz=UTC),
        )

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_res

        mock_querier.return_value.get_consumers_reservations_full.side_effect = mock_gen
        response = self.client.get("/consumers/me/reservations")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ReservationsQuerier")
    def test_get_streaks(self, mock_querier: MagicMock) -> None:
        """Test collection streaks."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_res = MockModel(
            collected_at=datetime.now(tz=UTC),
            window_start=datetime.now(tz=UTC),
            window_end=datetime.now(tz=UTC),
        )

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_res

        mock_querier.return_value.get_consumers_reservations_full.side_effect = mock_gen
        response = self.client.get("/consumers/me/streaks")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.BadgeQuerier")
    def test_get_consumer_badges(self, mock_querier: MagicMock) -> None:
        """Test get badges."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth
        mock_badge = MockModel(badge_id=1, level=1, name="N", description="D")

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_badge

        mock_querier.return_value.get_consumer_badges.side_effect = mock_gen
        response = self.client.get("/consumers/me/badges")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[consumer_auth]
