"""Tests for security and sensitive information manipulation."""

import json
from collections.abc import AsyncGenerator
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException, status
from internal.auth.security import (
    LogData,
    UpdatePasswordForm,
    check_password,
    generate_claim_code,
    generate_token,
    get_user_from_token,
    hash_password,
    log_request,
    log_to_db,
    sanitize_body,
    update_pw,
)
from internal.queries.models import UserRole
from pydantic import SecretStr
from sqlalchemy.exc import SQLAlchemyError

# Constants to satisfy magic number linter
TEST_USER_ID = 10
TOKEN_LENGTH = 43  # token_urlsafe(32) produces a 43-character string
CLAIM_CODE_LENGTH = 5

DUMMY_PASSWORD = "irunoutoffandoms"  # noqa: S105
WRONG_PASSWORD = "wrong_password"  # noqa: S105
OLD_PASSWORD_VAL = "old_password"  # noqa: S105
NEW_PASSWORD_VAL = "new_password"  # noqa: S105
CORRECT_OLD_PASSWORD_VAL = "correct_old_password"  # noqa: S105
WRONG_OLD_PASSWORD_VAL = "wrong_old_password"  # noqa: S105


class TestSecurity(IsolatedAsyncioTestCase):
    """Test suite for security and password functionality."""

    def test_hash_and_check_password(self) -> None:  # noqa: PLR6301
        """Test hashing and checking a password."""
        hashed = hash_password(DUMMY_PASSWORD)
        assert isinstance(hashed, str)
        assert check_password(DUMMY_PASSWORD, hashed)
        assert not check_password(WRONG_PASSWORD, hashed)

    def test_generate_token(self) -> None:  # noqa: PLR6301
        """Test generating a token."""
        token = generate_token()
        assert isinstance(token, str)
        assert len(token) == TOKEN_LENGTH

    def test_generate_claim_code(self) -> None:  # noqa: PLR6301
        """Test generating a claim code."""
        code = generate_claim_code([])
        assert isinstance(code, str)
        assert len(code) == CLAIM_CODE_LENGTH

    def test_generate_claim_code_avoid_used(self) -> None:  # noqa: PLR6301
        """Test generating a claim code avoiding used codes."""
        code1 = generate_claim_code([])
        code2 = generate_claim_code([code1])
        assert code1 != code2

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.TokenQuerier")
    async def test_get_user_from_token_success(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test extracting user object from valid auth token."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            conn = MagicMock()
            conn.commit = AsyncMock()
            yield conn

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_session = MagicMock()
        mock_session.user_id = TEST_USER_ID
        mock_session.role = UserRole.CONSUMER
        mock_querier.return_value.get_session_by_token = AsyncMock(
            return_value=mock_session
        )

        user_id, role = await get_user_from_token("token")

        assert user_id == TEST_USER_ID
        assert role == UserRole.CONSUMER

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.TokenQuerier")
    async def test_get_user_from_token_not_found(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test failure when auth token doesn't exist."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            conn = MagicMock()
            conn.commit = AsyncMock()
            yield conn

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_querier.return_value.get_session_by_token = AsyncMock(return_value=None)

        user_id, role = await get_user_from_token("token")

        assert user_id is None
        assert role is None

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.TokenQuerier")
    async def test_get_user_from_token_db_error(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test graceful failing when the database throws an error."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            conn = MagicMock()
            conn.commit = AsyncMock()
            yield conn

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_querier.return_value.get_session_by_token = AsyncMock(
            side_effect=SQLAlchemyError()
        )

        user_id, role = await get_user_from_token("token")
        assert user_id is None
        assert role is None

    @patch("internal.auth.security.check_password")
    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_success(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_check: MagicMock
    ) -> None:
        """Test updating a password successfully."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_querier.return_value.get_user_login = AsyncMock(return_value=mock_user)
        mock_querier.return_value.update_user_password = AsyncMock(
            return_value=mock_user
        )
        mock_check.return_value = True

        form = UpdatePasswordForm(
            old_password=SecretStr(CORRECT_OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        updated_user = await update_pw("test@test.com", form, mock_conn)

        assert updated_user.user_id == TEST_USER_ID

    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_user_not_found(self, mock_querier: MagicMock) -> None:
        """Test updating password fails if user doesn't exist."""
        mock_conn = MagicMock()
        mock_querier.return_value.get_user_login = AsyncMock(return_value=None)

        form = UpdatePasswordForm(
            old_password=SecretStr(OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        with self.assertRaises(HTTPException) as context:
            await update_pw("test@test.com", form, mock_conn)

        assert context.exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch("internal.auth.security.check_password")
    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_wrong_old_password(
        self, mock_querier: MagicMock, mock_check: MagicMock
    ) -> None:
        """Test updating password fails if old password is bad."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_querier.return_value.get_user_login = AsyncMock(return_value=mock_user)
        mock_check.return_value = False

        form = UpdatePasswordForm(
            old_password=SecretStr(WRONG_OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        with self.assertRaises(HTTPException) as context:
            await update_pw("test@test.com", form, mock_conn)

        assert context.exception.status_code == status.HTTP_403_FORBIDDEN

    @patch("internal.auth.security.check_password")
    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_db_error(
        self, mock_querier: MagicMock, mock_check: MagicMock
    ) -> None:
        """Test updating password fails if database insert fails."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_querier.return_value.get_user_login = AsyncMock(return_value=mock_user)
        mock_querier.return_value.update_user_password = AsyncMock(return_value=None)
        mock_check.return_value = True

        form = UpdatePasswordForm(
            old_password=SecretStr(CORRECT_OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        with self.assertRaises(HTTPException) as context:
            await update_pw("test@test.com", form, mock_conn)

        assert context.exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_sanitize_body(self) -> None:  # noqa: PLR6301
        """Test redacting sensitive fields from logging output."""
        body: dict[str, object] = {
            "password": "secret_password",
            "email": "test@test.com",
            "safe_data": "visible_data",
        }
        sanitized = sanitize_body(body)

        assert sanitized["password"] == "REDACTED"  # noqa: S105
        assert sanitized["email"] == "REDACTED"
        assert sanitized["safe_data"] == "visible_data"

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.ActivityLogQuerier")
    async def test_log_to_db_success(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test successfully logging request data to database."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            conn = MagicMock()
            conn.commit = AsyncMock()
            yield conn

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_querier.return_value.create_activity_log = AsyncMock()

        log_data = LogData(
            user_id=TEST_USER_ID,
            user_role=UserRole.CONSUMER,
            method="GET",
            path="/test",
            query_params={},
            ip_address="127.0.0.1",
            body=None,
        )

        await log_to_db(log_data)

        mock_querier.return_value.create_activity_log.assert_called_once()

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.ActivityLogQuerier")
    async def test_log_to_db_failure(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test graceful failing when activity log db insert crashes."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            conn = MagicMock()
            conn.commit = AsyncMock()
            yield conn

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_querier.return_value.create_activity_log = AsyncMock(
            side_effect=SQLAlchemyError()
        )

        log_data = LogData(
            user_id=TEST_USER_ID,
            user_role=UserRole.CONSUMER,
            method="GET",
            path="/test",
            query_params={},
            ip_address="127.0.0.1",
            body=None,
        )

        # Should NOT raise an error
        await log_to_db(log_data)

    @patch("internal.auth.security.get_user_from_token")
    @patch("internal.auth.security.log_to_db")
    async def test_log_request_success(  # noqa: PLR6301
        self, mock_log: MagicMock, mock_get_user: MagicMock
    ) -> None:
        """Test intercepting and logging a standard FastAPI POST request."""
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.query_params = {"q": "1"}
        mock_request.client.host = "127.0.0.1"

        def mock_get_header(key: str, default: str = "") -> str | None:
            if key.lower() == "content-type":
                return "application/json"
            if key.lower() == "authorization":
                return "Bearer valid_token"
            return default

        mock_request.headers.get.side_effect = mock_get_header
        mock_request.json = AsyncMock(return_value={"password": "123", "data": "val"})

        # Make sure the user is returned as a tuple matching the new signature
        mock_get_user.return_value = (TEST_USER_ID, UserRole.CONSUMER)

        await log_request(mock_request)

        mock_log.assert_called_once()

        # log_to_db no longer receives `conn`, so log_data is now arg [0]
        log_data: LogData = mock_log.call_args[0][0]

        assert log_data.user_id == TEST_USER_ID
        assert log_data.method == "POST"
        assert isinstance(log_data.body, dict)
        assert log_data.body["password"] == "REDACTED"  # noqa: S105
        assert log_data.body["data"] == "val"

    @patch("internal.auth.security.log_to_db")
    async def test_log_request_no_token_invalid_json(self, mock_log: MagicMock) -> None:  # noqa: PLR6301
        """Test intercepting a request lacking a token and containing invalid JSON."""
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.query_params = {}
        mock_request.client.host = "127.0.0.1"

        mock_request.headers.get.side_effect = lambda k, d="": d

        mock_request.json = AsyncMock(side_effect=json.JSONDecodeError("msg", "doc", 0))

        await log_request(mock_request)
        mock_log.assert_called_once()
