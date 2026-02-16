"""Tests for consumer endpoints."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import consumer_auth
from main import app

# Constants to satisfy magic number linter (PLR2004)
TEST_RESERVATION_ID = 101
TEST_BUNDLE_ID = 5

def override_consumer_auth() -> MagicMock:
    """Mock the consumer authentication dependency.

    Returns:
        MagicMock: A mock object for consumer authentication.
    """
    return MagicMock()


class TestConsumers(unittest.TestCase):
    """Test suite for consumer-related functionality."""

    @staticmethod
    def test_register_consumer(client: TestClient) -> None:
        """Test consumer registration."""
        with patch("routers.consumers.create_consumer") as mock_create:
            mock_create.return_value = True

            payload = {
                "email": "consumer@test.com",
                "password": "securepass",
                "first_name": "Furkan",
                "last_name": "RuggedHill",
            }

            response = client.post("/consumers", json=payload)

            assert response.status_code == status.HTTP_201_CREATED  # noqa: S101
            mock_create.assert_called_once()

    @patch("routers.consumers.ReservationsQuerier")
    @staticmethod
    def test_get_my_reservations(mock_querier: MagicMock, client: TestClient) -> None:
        """Test getting logged-in user's reservations."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_res = MagicMock(
            reservation_id=TEST_RESERVATION_ID,
            bundle_id=TEST_BUNDLE_ID
        )
        mock_querier.return_value.get_consumers_reservations.return_value = [mock_res]

        response = client.get("/consumers/me/reservations")

        assert response.status_code == status.HTTP_200_OK  # noqa: S101
        assert len(response.json()) == 1  # noqa: S101
        assert response.json()[0]["reservation_id"] == TEST_RESERVATION_ID  # noqa: S101

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ReservationsQuerier")
    @staticmethod
    def test_get_my_reservations_empty(mock_querier: MagicMock, client: TestClient) -> None:
        """Test 500 error when no reservations found (per implementation)."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_querier.return_value.get_consumers_reservations.return_value = []

        response = client.get("/consumers/me/reservations")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR  # noqa: S101
        assert "failed to get reservations" in response.json()["detail"]  # noqa: S101

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    @staticmethod
    def test_update_consumer(mock_querier: MagicMock, client: TestClient) -> None:
        """Test updating consumer profile."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_querier.return_value.update_consumer.return_value = True

        payload = {"first_name": "Who", "last_name": "should it be"}

        response = client.patch("/consumers/me", json=payload)

        assert response.status_code == status.HTTP_200_OK  # noqa: S101
        assert response.text == '"consumer was updated"'  # noqa: S101

        del app.dependency_overrides[consumer_auth]

    @patch("routers.consumers.ConsumerQuerier")
    @staticmethod
    def test_update_consumer_fail(mock_querier: MagicMock, client: TestClient) -> None:
        """Test failure when updating consumer profile."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_querier.return_value = None

        payload = {"first_name": "X", "last_name": "Y"}

        response = client.patch("/consumers/me", json=payload)

        print(type(response.status_code))  # Debugging line to check type of status code
        assert response.status_code() == status.HTTP_500_INTERNAL_SERVER_ERROR  # noqa: S101

        del app.dependency_overrides[consumer_auth]


if __name__ == "__main__":
    unittest.main()
