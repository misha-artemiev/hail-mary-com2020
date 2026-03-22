"""Tests for user endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import bearer_auth
from main import app
from testing.test_database import cleanup_database, init_database

# Constants to satisfy magic number linter
TEST_USER_ID = 10
TEST_OLD_EMAIL = "old@test.com"
TEST_NEW_EMAIL = "gold@test.com"


def override_bearer_auth() -> MagicMock:
    """Mock the bearer authentication dependency.

    Returns:
        MagicMock: Mock Object simulator for an active user session.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    mock.email = TEST_OLD_EMAIL
    return mock


class TestUsers(TestCase):
    """Test suite for user-related functionality."""

    def setUp(self) -> None:
        """Runs before every test to set up the client."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to tear down the client."""
        del self.client
        cleanup_database()

    @patch("routers.users.update_pw")
    def test_update_password(self, mock_update_pw: MagicMock) -> None:
        """Test updating the user's password."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        # Mock the async security function
        mock_update_pw.side_effect = AsyncMock(return_value=True)

        # Assuming UpdatePasswordForm takes these typical fields.
        # If your actual form expects different keys, adjust them here!
        payload = {"old_password": "1234", "new_password": "GOPLAYDISCOELYSIUMRIGHTNOW"}

        response = self.client.patch("/users/me/password", json=payload)

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_update_pw.assert_called_once()

        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_update_email_success(self, mock_querier: MagicMock) -> None:
        """Test successfully updating the user's email."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        mock_instance = mock_querier.return_value

        # Simulating a returned user row after successful update
        mock_user_row = MagicMock()
        mock_instance.update_user_email = AsyncMock(return_value=mock_user_row)

        # In your route, `email` is a scalar query parameter, not a JSON body.
        response = self.client.patch(
            "/users/me/email", params={"email": TEST_NEW_EMAIL}
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_update_email_fail(self, mock_querier: MagicMock) -> None:
        """Test failure when updating the user's email."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        mock_instance = mock_querier.return_value

        # Simulating a database failure or missing user (returns None)
        mock_instance.update_user_email = AsyncMock(return_value=None)

        response = self.client.patch(
            "/users/me/email", params={"email": TEST_NEW_EMAIL}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "update users email" in response.json()["detail"].lower()

        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.InboxQuerier")
    def test_get_inbox(self, mock_querier: MagicMock) -> None:
        """Test getting the user's inbox."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_instance = mock_querier.return_value

        mock_inbox = MagicMock()
        mock_inbox.message_id = 1
        mock_inbox.user_id = TEST_USER_ID
        mock_inbox.sender_id = 99
        mock_inbox.message_subject = "Subject"
        mock_inbox.message_text = "17"

        async def mock_generator(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield mock_inbox

        mock_instance.get_user_inbox.side_effect = mock_generator

        response = self.client.get("/users/me/inbox")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.InboxQuerier")
    def test_send_message(self, mock_querier: MagicMock) -> None:
        """Test sending an inbox message."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_instance = mock_querier.return_value

        mock_inbox = MagicMock()
        mock_inbox.message_id = 1
        mock_inbox.user_id = 2
        mock_inbox.sender_id = TEST_USER_ID
        mock_inbox.message_subject = "Subject"
        mock_inbox.message_text = "17"
        mock_instance.create_inbox_message = AsyncMock(return_value=mock_inbox)

        payload = {"user_id": 2, "message_subject": "Subject", "message_text": "17"}

        response = self.client.post("/users/me/inbox", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message_subject"] == "Subject"

        del app.dependency_overrides[bearer_auth]
