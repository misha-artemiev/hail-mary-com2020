"""Tests for security and sensitive information manipulation."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException, status
from internal.auth.security import (
    UpdatePasswordForm,
    check_password,
    generate_claim_code,
    generate_token,
    hash_password,
    update_pw,
)
from pydantic import SecretStr

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
        used_codes = ["AAA11", "BBB22"]

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

        # Mock finding the user
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

        # Mock finding the user with a specific password hash
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
