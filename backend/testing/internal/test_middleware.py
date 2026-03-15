"""Tests for authentication middlewares."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasicCredentials
from internal.auth.middleware import (
    admin_auth,
    basic_auth,
    bearer_auth,
    consumer_auth,
    root_auth,
    seller_auth,
)
from internal.queries.models import UserRole

# Constants
TEST_USER_ID = 10
DUMMY_PASSWORD = "pew"  # noqa: S105


class TestMiddleware(IsolatedAsyncioTestCase):
    """Test suite for auto authorisation middlewares."""

    @patch("internal.auth.middleware.check_password")
    @patch("internal.auth.middleware.UserQuerier")
    async def test_basic_auth_success(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_check: MagicMock
    ) -> None:
        """Test basic auth parses credentials and returns user response."""
        mock_conn = MagicMock()
        mock_creds = HTTPBasicCredentials(username="test@test.com", password=DUMMY_PASSWORD)  # noqa: E501

        # Mock User
        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.role = UserRole.CONSUMER
        mock_querier.return_value.get_user_login = AsyncMock(return_value=mock_user)

        # Mock password verification
        mock_check.return_value = True

        response = await basic_auth(mock_conn, mock_creds)

        assert response.user_id == TEST_USER_ID
        assert response.role == UserRole.CONSUMER

    @patch("internal.auth.middleware.AdminQuerier")
    @patch("internal.auth.middleware.check_password")
    @patch("internal.auth.middleware.UserQuerier")
    async def test_basic_auth_admin_deactivated(
        self, mock_user_q: MagicMock, mock_check: MagicMock, mock_admin_q: MagicMock
    ) -> None:
        """Test basic auth fails for a deactivated admin."""
        mock_conn = MagicMock()
        mock_creds = HTTPBasicCredentials(username="admin@test.com", password=DUMMY_PASSWORD)  # noqa: E501

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.role = UserRole.ADMIN
        mock_user_q.return_value.get_user_login = AsyncMock(return_value=mock_user)
        mock_check.return_value = True

        mock_admin = MagicMock()
        mock_admin.active = False
        mock_admin_q.return_value.get_admin = AsyncMock(return_value=mock_admin)

        with self.assertRaises(HTTPException) as context:
            await basic_auth(mock_conn, mock_creds)

        assert context.exception.status_code == status.HTTP_403_FORBIDDEN
        assert "deactivated" in context.exception.detail

    @patch("internal.auth.middleware.TokenQuerier")
    async def test_bearer_auth_success(self, mock_querier: MagicMock) -> None:  # noqa: PLR6301
        """Test bearer auth retrieves a valid session."""
        mock_conn = MagicMock()
        mock_creds = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="token123"
        )

        mock_session = MagicMock()
        mock_session.user_id = TEST_USER_ID
        mock_querier.return_value.get_session_by_token = AsyncMock(
            return_value=mock_session
        )

        session = await bearer_auth(mock_conn, mock_creds)

        assert session.user_id == TEST_USER_ID

    def test_consumer_auth_success(self) -> None:  # noqa: PLR6301
        """Test consumer role authorisation."""
        mock_session = MagicMock()
        mock_session.role = UserRole.CONSUMER

        session = consumer_auth(mock_session)
        assert session == mock_session

    def test_consumer_auth_failure(self) -> None:
        """Test consumer role authorisation failure."""
        mock_session = MagicMock()
        mock_session.role = UserRole.SELLER

        with self.assertRaises(HTTPException) as context:
            consumer_auth(mock_session)

        assert context.exception.status_code == status.HTTP_403_FORBIDDEN

    def test_seller_auth_success(self) -> None:  # noqa: PLR6301
        """Test seller role authorisation."""
        mock_session = MagicMock()
        mock_session.role = UserRole.SELLER

        session = seller_auth(mock_session)
        assert session == mock_session

    @patch("internal.auth.middleware.AdminQuerier")
    async def test_admin_auth_success(self, mock_querier: MagicMock) -> None:  # noqa: PLR6301
        """Test admin role authorisation success."""
        mock_conn = MagicMock()
        mock_session = MagicMock()
        mock_session.role = UserRole.ADMIN
        mock_session.user_id = TEST_USER_ID

        mock_admin = MagicMock()
        mock_admin.active = True
        mock_querier.return_value.get_admin = AsyncMock(return_value=mock_admin)

        session = await admin_auth(mock_conn, mock_session)
        assert session == mock_session

    @patch("internal.auth.middleware.AdminQuerier")
    async def test_admin_auth_deactivated(self, mock_querier: MagicMock) -> None:
        """Test admin role authorisation fails when admin is deactivated."""
        mock_conn = MagicMock()
        mock_session = MagicMock()
        mock_session.role = UserRole.ADMIN
        mock_session.user_id = TEST_USER_ID

        mock_admin = MagicMock()
        mock_admin.active = False
        mock_querier.return_value.get_admin = AsyncMock(return_value=mock_admin)

        with self.assertRaises(HTTPException) as context:
            await admin_auth(mock_conn, mock_session)

        assert context.exception.status_code == status.HTTP_403_FORBIDDEN

    @patch("internal.auth.middleware.auth_settings")
    def test_root_auth_success(self, mock_settings: MagicMock) -> None:  # noqa: PLR6301
        """Test root authentication success."""
        mock_settings.root_username = "root"
        mock_settings.root_password = "password"  # noqa: S105

        creds = HTTPBasicCredentials(username="root", password="password")  # noqa: S106
        # Should not raise an exception
        root_auth(creds)

    @patch("internal.auth.middleware.auth_settings")
    def test_root_auth_failure(self, mock_settings: MagicMock) -> None:
        """Test root authentication failure with wrong credentials."""
        mock_settings.root_username = "root"
        mock_settings.root_password = "password"  # noqa: S105

        creds = HTTPBasicCredentials(username="wrong", password="password")  # noqa: S106

        with self.assertRaises(HTTPException) as context:
            root_auth(creds)

        assert context.exception.status_code == status.HTTP_401_UNAUTHORIZED
