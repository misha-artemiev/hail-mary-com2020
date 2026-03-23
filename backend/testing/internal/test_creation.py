"""Tests for user/consumer/seller/admin creation functions."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from internal.auth.creation import (
    CreateAdminForm,
    CreateConsumerForm,
    CreateSellerForm,
    create_admin,
    create_consumer,
    create_seller,
    create_user,
)
from internal.queries.models import UserRole
from pydantic import EmailStr, SecretStr


class TestCreateUser(IsolatedAsyncioTestCase):
    """Test suite for create_user function."""

    @patch("internal.auth.creation.UserQuerier")
    @patch("internal.auth.creation.hash_password")
    async def test_create_user_success(  # noqa: PLR6301
        self, mock_hash: MagicMock, mock_querier: MagicMock
    ) -> None:
        """Test create_user inserts user and returns row."""
        mock_conn = MagicMock()
        mock_hash.return_value = "hashed_pw"
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_querier.return_value.create_user = AsyncMock(return_value=mock_user)

        result = await create_user(
            username="testuser",
            email="test@test.com",
            password=SecretStr("password123"),
            role=UserRole.CONSUMER,
            conn=mock_conn,
        )

        assert result.user_id == 1
        mock_querier.return_value.create_user.assert_called_once()

    @patch("internal.auth.creation.UserQuerier")
    @patch("internal.auth.creation.hash_password")
    async def test_create_user_failure(
        self, mock_hash: MagicMock, mock_querier: MagicMock
    ) -> None:
        """Test create_user raises ValueError on failure."""
        mock_conn = MagicMock()
        mock_hash.return_value = "hashed_pw"
        mock_querier.return_value.create_user = AsyncMock(return_value=None)

        with self.assertRaises(ValueError):
            await create_user(
                username="testuser",
                email="test@test.com",
                password=SecretStr("password123"),
                role=UserRole.CONSUMER,
                conn=mock_conn,
            )


class TestCreateConsumer(IsolatedAsyncioTestCase):
    """Test suite for create_consumer function."""

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.ConsumerQuerier")
    async def test_create_consumer_success(  # noqa: PLR6301
        self, mock_consumer_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_consumer creates consumer and user."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user

        mock_consumer = MagicMock()
        mock_consumer.user_id = 1
        mock_consumer_q.return_value.create_consumer = AsyncMock(
            return_value=mock_consumer
        )

        form = CreateConsumerForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            first_name="John",
            last_name="Doe",
        )

        result = await create_consumer(form, mock_conn)

        assert result.user_id == 1
        mock_create_user.assert_called_once()
        mock_consumer_q.return_value.create_consumer.assert_called_once()

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.ConsumerQuerier")
    async def test_create_consumer_failure(
        self, mock_consumer_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_consumer raises ValueError on failure."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user
        mock_consumer_q.return_value.create_consumer = AsyncMock(return_value=None)

        form = CreateConsumerForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            first_name="John",
            last_name="Doe",
        )

        with self.assertRaises(ValueError):
            await create_consumer(form, mock_conn)


class TestCreateSeller(IsolatedAsyncioTestCase):
    """Test suite for create_seller function."""

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.SellerQuerier")
    async def test_create_seller_success(  # noqa: PLR6301
        self, mock_seller_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_seller creates seller and user."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user

        mock_seller = MagicMock()
        mock_seller.user_id = 1
        mock_seller_q.return_value.create_seller = AsyncMock(return_value=mock_seller)

        form = CreateSellerForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            seller_name="Test Shop",
            address_line1="123 Main St",
            city="Test City",
            post_code="12345",
            country="Test Country",
            latitude=40.7128,
            longitude=-74.0060,
        )

        result = await create_seller(form, mock_conn)

        assert result.user_id == 1
        mock_create_user.assert_called_once()
        mock_seller_q.return_value.create_seller.assert_called_once()

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.SellerQuerier")
    async def test_create_seller_failure(
        self, mock_seller_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_seller raises ValueError on failure."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user
        mock_seller_q.return_value.create_seller = AsyncMock(return_value=None)

        form = CreateSellerForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            seller_name="Test Shop",
            address_line1="123 Main St",
            city="Test City",
            post_code="12345",
            country="Test Country",
            latitude=40.7128,
            longitude=-74.0060,
        )

        with self.assertRaises(ValueError):
            await create_seller(form, mock_conn)


class TestCreateAdmin(IsolatedAsyncioTestCase):
    """Test suite for create_admin function."""

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.AdminQuerier")
    async def test_create_admin_success(  # noqa: PLR6301
        self, mock_admin_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_admin creates admin and user."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user

        mock_admin = MagicMock()
        mock_admin.user_id = 1
        mock_admin_q.return_value.create_admin = AsyncMock(return_value=mock_admin)

        form = CreateAdminForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            first_name="John",
            last_name="Doe",
        )

        result = await create_admin(form, mock_conn)

        assert result.user_id == 1
        mock_create_user.assert_called_once()
        mock_admin_q.return_value.create_admin.assert_called_once()

    @patch("internal.auth.creation.create_user")
    @patch("internal.auth.creation.AdminQuerier")
    async def test_create_admin_failure(
        self, mock_admin_q: MagicMock, mock_create_user: MagicMock
    ) -> None:
        """Test create_admin raises ValueError on failure."""
        mock_conn = MagicMock()
        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_create_user.return_value = mock_user
        mock_admin_q.return_value.create_admin = AsyncMock(return_value=None)

        form = CreateAdminForm(
            username="testuser",
            email=EmailStr("test@test.com"),
            password=SecretStr("password123"),
            first_name="John",
            last_name="Doe",
        )

        with self.assertRaises(ValueError):
            await create_admin(form, mock_conn)


TestCreation = TestCreateUser
