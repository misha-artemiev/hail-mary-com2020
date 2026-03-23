"""Tests for user endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import bearer_auth
from main import app
from testing.test_database import cleanup_database, init_database

TEST_USER_ID = 10


class MockModel:
    """Mock models for user validation."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401, D107
        self.user_id = TEST_USER_ID
        self.consumer_id = TEST_USER_ID
        self.username = "u"
        self.email = "e@e.com"
        self.role = "consumer"
        self.message_id = 1
        self.sender_id = 1
        self.message_subject = "S"
        self.message_text = "T"
        self.is_read = False
        self.read_status = False
        self.sent_at = datetime.now(tz=UTC)
        self.report_id = 1
        self.reservation_id = 1
        self.issue_type = "OTHER"
        self.description = "D"
        self.status = "open"
        self.created_at = datetime.now(tz=UTC)
        self.__dict__.update(kwargs)


def override_bearer_auth() -> MagicMock:
    """Mock auth."""  # noqa: DOC201
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    mock.email = "e@e.com"
    return mock


class TestUsers(TestCase):
    """Test suite."""

    def setUp(self) -> None:  # noqa: D102
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:  # noqa: D102
        del self.client
        cleanup_database()

    @patch("routers.users.update_pw", new_callable=AsyncMock)
    def test_update_password(self, mock_update: AsyncMock) -> None:
        """Test password update."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_update.return_value = True
        response = self.client.patch(
            "/users/me/password", json={"old_password": "a", "new_password": "b"}
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_update_email(self, mock_querier: MagicMock) -> None:
        """Test email update."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_querier.return_value.update_user_email = AsyncMock(
            return_value=MockModel()
        )
        # BUG FIX: source takes `email` as a query parameter, not a JSON body field
        response = self.client.patch("/users/me/email", params={"email": "new@e.com"})
        assert response.status_code == status.HTTP_202_ACCEPTED
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_update_email_fail(self, mock_querier: MagicMock) -> None:
        """Test email fail."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_querier.return_value.update_user_email = AsyncMock(return_value=None)
        # BUG FIX: source takes `email` as a query parameter, not a JSON body field
        response = self.client.patch("/users/me/email", params={"email": "new@e.com"})
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.InboxQuerier")
    def test_get_user_inbox(self, mock_querier: MagicMock) -> None:
        """Test get inbox."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield MockModel()

        mock_querier.return_value.get_user_inbox.side_effect = mock_gen
        response = self.client.get("/users/me/inbox")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.InboxQuerier")
    def test_send_message(self, mock_querier: MagicMock) -> None:
        """Test send message."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_querier.return_value.create_inbox_message = AsyncMock(
            return_value=MockModel()
        )
        response = self.client.post(
            "/users/me/inbox",
            json={"user_id": 1, "message_subject": "S", "message_text": "T"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.InboxQuerier")
    def test_mark_inbox_message_as_read(self, mock_querier: MagicMock) -> None:
        """Test read message."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield MockModel(message_id=1)

        mock_querier.return_value.get_user_inbox.side_effect = mock_gen
        mock_querier.return_value.read_inbox_message = AsyncMock(
            return_value=MockModel(is_read=True, read_status=True)
        )
        response = self.client.patch("/users/me/inbox/1")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_get_user_id_success(self, mock_querier: MagicMock) -> None:
        """Test get id."""
        mock_querier.return_value.get_user_id = AsyncMock(return_value=MockModel())
        response = self.client.get("/users/id/test")
        assert response.status_code == status.HTTP_200_OK

    @patch("routers.users.AdminIssueReportsQuerier")
    def test_create_admin_issue_report(self, mock_querier: MagicMock) -> None:
        """Test create report."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_querier.return_value.create_admin_issue_report = AsyncMock(
            return_value=MockModel()
        )
        response = self.client.post(
            "/users/me/reports/admin",
            json={"issue_type": "APP_CRASH", "description": "Bug"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.SellerIssueReportsQuerier")
    @patch("routers.users.ReservationsQuerier")
    def test_create_seller_issue_report(
        self, mock_res_querier: MagicMock, mock_report_querier: MagicMock
    ) -> None:
        """Test create seller report.

        BUG FIX: reservation_id is a path parameter on
        /me/reports/seller/{reservation_id}, not a JSON body field.
        Source also calls get_reservation, not get_consumer_reservation.
        """
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_reservation = MockModel()
        mock_reservation.consumer_id = TEST_USER_ID
        # BUG FIX: source calls get_reservation, not get_consumer_reservation
        mock_res_querier.return_value.get_reservation = AsyncMock(
            return_value=mock_reservation
        )
        mock_report_querier.return_value.create_seller_issue_report = AsyncMock(
            return_value=MockModel()
        )
        # BUG FIX: reservation_id goes in the URL path, not the request body
        response = self.client.post(
            "/users/me/reports/seller/1",
            json={"issue_type": "OTHER", "description": "Bad"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.ReservationsQuerier")
    def test_create_seller_issue_report_not_found(
        self, mock_res_querier: MagicMock
    ) -> None:
        """Test seller report returns 404 when reservation does not exist."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_res_querier.return_value.get_reservation = AsyncMock(return_value=None)
        response = self.client.post(
            "/users/me/reports/seller/1",
            json={"issue_type": "OTHER", "description": "Bad"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.ReservationsQuerier")
    def test_create_seller_issue_report_not_owned(
        self, mock_res_querier: MagicMock
    ) -> None:
        """Test seller report returns 404 when reservation belongs to a different user."""  # noqa: E501
        app.dependency_overrides[bearer_auth] = override_bearer_auth
        mock_reservation = MockModel()
        mock_reservation.consumer_id = TEST_USER_ID + 99  # different user
        mock_res_querier.return_value.get_reservation = AsyncMock(
            return_value=mock_reservation
        )
        response = self.client.post(
            "/users/me/reports/seller/1",
            json={"issue_type": "OTHER", "description": "Bad"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.UserQuerier")
    def test_get_user_id_not_found(self, mock_querier: MagicMock) -> None:
        """Test get user id returns 404 when user does not exist."""
        mock_querier.return_value.get_user_id = AsyncMock(return_value=None)
        response = self.client.get("/users/id/unknown")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("routers.users.AdminIssueReportsQuerier")
    def test_get_admin_issue_reports(self, mock_querier: MagicMock) -> None:
        """Test get admin reports."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield MockModel()

        mock_querier.return_value.get_admin_issue_reports_by_user.side_effect = mock_gen
        response = self.client.get("/users/me/reports/admin")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[bearer_auth]

    @patch("routers.users.SellerIssueReportsQuerier")
    def test_get_seller_issue_reports(self, mock_querier: MagicMock) -> None:
        """Test get seller reports."""
        app.dependency_overrides[bearer_auth] = override_bearer_auth

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield MockModel()

        mock_querier.return_value.get_seller_issue_reports_by_user.side_effect = (
            mock_gen
        )
        response = self.client.get("/users/me/reports/seller")
        assert response.status_code == status.HTTP_200_OK
        del app.dependency_overrides[bearer_auth]
