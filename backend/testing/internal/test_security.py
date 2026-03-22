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

# Constants to fix S106 (Hardcoded password string passed to function arguments)
DUMMY_PASSWORD = "irunoutoffandoms"  # noqa: S105
WRONG_PASSWORD = "wrong_password"  # noqa: S105
OLD_PASSWORD_VAL = "old_password"  # noqa: S105
NEW_PASSWORD_VAL = "new_password"  # noqa: S105
CORRECT_OLD_PASSWORD_VAL = "correct_old_password"  # noqa: S105
WRONG_OLD_PASSWORD_VAL = "wrong_old_password"  # noqa: S105


class TestSecurity(IsolatedAsyncioTestCase):
    """Test suite for security and password functionality."""

    def test_hash_and_check_password(self) -> None:  # noqa: PLR6301
        """Test that hashing and checking a password works correctly."""
        hashed = hash_password(DUMMY_PASSWORD)

        assert hashed != DUMMY_PASSWORD
        assert isinstance(hashed, str)

        is_valid = check_password(DUMMY_PASSWORD, hashed)
        assert is_valid is True

        is_invalid = check_password(WRONG_PASSWORD, hashed)
        assert is_invalid is False

    def test_generate_token(self) -> None:  # noqa: PLR6301
        """Test secure token generation."""
        token1 = generate_token()
        token2 = generate_token()

        assert len(token1) >= TOKEN_LENGTH
        assert token1 != token2

    def test_generate_claim_code(self) -> None:  # noqa: PLR6301
        """Test generation of unique claim codes."""
        used_codes = ["AA-11", "BB-22"]

        code = generate_claim_code(used_codes)

        assert isinstance(code, str)
        assert len(code) == CLAIM_CODE_LENGTH
        assert "-" in code
        assert code not in used_codes

    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_success(self, mock_querier: MagicMock) -> None:  # noqa: PLR6301
        """Test successfully updating a user's password."""
        mock_conn = MagicMock()
        mock_instance = mock_querier.return_value

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.pw_hash = hash_password(OLD_PASSWORD_VAL)
        mock_instance.get_user_login = AsyncMock(return_value=mock_user)

        mock_updated = MagicMock()
        mock_instance.update_user_password = AsyncMock(return_value=mock_updated)

        form = UpdatePasswordForm(
            old_password=SecretStr(OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        result = await update_pw("inspector@morse.com", form, mock_conn)

        assert result == mock_updated

    @patch("internal.auth.security.UserQuerier")
    async def test_update_pw_wrong_old_password(self, mock_querier: MagicMock) -> None:
        """Test updating password fails with incorrect old password."""
        mock_conn = MagicMock()
        mock_instance = mock_querier.return_value

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.pw_hash = hash_password(CORRECT_OLD_PASSWORD_VAL)
        mock_instance.get_user_login = AsyncMock(return_value=mock_user)

        form = UpdatePasswordForm(
            old_password=SecretStr(WRONG_OLD_PASSWORD_VAL),
            new_password=SecretStr(NEW_PASSWORD_VAL),
        )

        with self.assertRaises(HTTPException) as context:
            await update_pw("inspector@morse.com", form, mock_conn)

        assert context.exception.status_code == status.HTTP_403_FORBIDDEN
        assert "Old password is incorrect" in context.exception.detail

    # --- NEW ACTIVITY LOGGING TESTS ---

    def test_sanitize_body(self) -> None:  # noqa: PLR6301
        """Test sensitive fields are correctly redacted."""
        body: dict[str, object] = {
            "username": "test_user",
            "password": "supersecretpassword",
            "TOKEN": "12345abcd",
            "normal_field": "safe",
        }

        redacted = sanitize_body(body)

        assert redacted["username"] == "test_user"
        assert redacted["normal_field"] == "safe"
        assert redacted["password"] == "REDACTED"  # noqa: S105
        assert redacted["TOKEN"] == "REDACTED"  # noqa: S105

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.TokenQuerier")
    async def test_get_user_from_token_success(  # noqa: PLR6301
        self, mock_tq: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test retrieving user_id and role from a valid token."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield AsyncMock()

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_session = MagicMock()
        mock_session.user_id = TEST_USER_ID
        mock_session.role = UserRole.CONSUMER
        mock_tq.return_value.get_session_by_token = AsyncMock(return_value=mock_session)

        uid, role = await get_user_from_token("valid_token")

        assert uid == TEST_USER_ID
        assert role == UserRole.CONSUMER

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.TokenQuerier")
    async def test_get_user_from_token_db_error(  # noqa: PLR6301
        self, mock_tq: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test safe failure when DB lookup raises a SQLAlchemyError."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield AsyncMock()

        mock_db.get_connection.side_effect = mock_conn_gen

        mock_tq.return_value.get_session_by_token.side_effect = SQLAlchemyError()

        uid, role = await get_user_from_token("valid_token")

        assert uid is None
        assert role is None

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.ActivityLogQuerier")
    async def test_log_to_db_success(  # noqa: PLR6301
        self, mock_aq: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test successfully inserting an activity log into the DB."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            # Use AsyncMock so await conn.commit() succeeds!
            yield AsyncMock()

        mock_db.get_connection.side_effect = mock_conn_gen
        mock_aq.return_value.create_activity_log = AsyncMock()

        data = LogData(
            user_id=TEST_USER_ID,
            user_role=UserRole.CONSUMER,
            method="POST",
            path="/test",
            query_params={},
            ip_address="127.0.0.1",
            body={"test": "data"},
        )

        await log_to_db(data)

        mock_aq.return_value.create_activity_log.assert_called_once()

    @patch("internal.auth.security.database_manager")
    @patch("internal.auth.security.ActivityLogQuerier")
    async def test_log_to_db_error(  # noqa: PLR6301
        self, mock_aq: MagicMock, mock_db: MagicMock
    ) -> None:
        """Test DB insert failures are caught and don't crash the server."""

        async def mock_conn_gen() -> AsyncGenerator[Any]:  # noqa: RUF029
            yield AsyncMock()

        mock_db.get_connection.side_effect = mock_conn_gen
        mock_aq.return_value.create_activity_log.side_effect = SQLAlchemyError()

        data = LogData(
            user_id=TEST_USER_ID,
            user_role=UserRole.CONSUMER,
            method="GET",
            path="/test",
            query_params={},
            ip_address="127.0.0.1",
            body=None,
        )

        # This should execute silently and not raise the DB exception upward
        await log_to_db(data)

    @patch("internal.auth.security.log_to_db")
    @patch("internal.auth.security.get_user_from_token")
    async def test_log_request_success(  # noqa: PLR6301
        self, mock_get_user: MagicMock, mock_log: MagicMock
    ) -> None:
        """Test intercepting and logging a standard FastAPI POST request."""
        mock_get_user.return_value = (TEST_USER_ID, UserRole.CONSUMER)

        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.query_params = {"q": "1"}
        mock_request.client.host = "127.0.0.1"
        mock_request.headers.get.return_value = "Bearer valid_token"
        mock_request.json = AsyncMock(return_value={"password": "123", "data": "val"})

        await log_request(mock_request)

        mock_log.assert_called_once()
        log_data: LogData = mock_log.call_args[0][0]

        assert log_data.user_id == TEST_USER_ID
        assert log_data.method == "POST"
        # Type guarding the dict to satisfy Pydantic/Mypy validation checks
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
        mock_request.headers.get.return_value = None

        # Simulating a bad request body that would trigger a JSON parsing failure
        mock_request.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        await log_request(mock_request)

        mock_log.assert_called_once()
        log_data: LogData = mock_log.call_args[0][0]

        assert log_data.user_id is None
        assert log_data.body is None
