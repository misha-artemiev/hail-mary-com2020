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


def override_consumer_auth() -> MagicMock:
    """Mock the consumer authentication dependency.

    Returns:
        MagicMock: Mock Object simualator.
    """
    return MagicMock()


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
