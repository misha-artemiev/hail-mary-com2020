"""Tests for seller, consumer and admin entity creation."""

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
from pydantic import SecretStr

# Constants
TEST_USER_ID = 10
TEST_LAT = 50.0
TEST_LON = -0.5


class TestCreation(IsolatedAsyncioTestCase):
    """Test suite for entity creation routines."""

    @patch("internal.auth.creation.hash_password")
    @patch("internal.auth.creation.UserQuerier")
    async def test_create_user_success(  # noqa: PLR6301
        self, mock_querier: MagicMock, mock_hash: MagicMock
    ) -> None:
        """Test base user creation."""
        mock_conn = MagicMock()
        mock_hash.return_value = "hashed_pass"

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_querier.return_value.create_user = AsyncMock(return_value=mock_user)

        user = await create_user(
            username="Endeavour",
            email="new@show.com",
            password=SecretStr("pass"),
            role=UserRole.CONSUMER,
            conn=mock_conn,
        )

        assert user.user_id == TEST_USER_ID

    @patch("internal.auth.creation.ConsumerQuerier")
    @patch("internal.auth.creation.create_user")
    async def test_create_consumer_success(  # noqa: PLR6301
        self, mock_create_user: MagicMock, mock_querier: MagicMock
    ) -> None:
        """Test creating a consumer and its base user."""
        mock_conn = MagicMock()

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_create_user.return_value = mock_user

        mock_consumer = MagicMock()
        mock_querier.return_value.create_consumer = AsyncMock(
            return_value=mock_consumer
        )

        form = CreateConsumerForm(
            username="consumer",
            email="c@test.com",
            password=SecretStr("pw"),
            first_name="John",
            last_name="Doe",
        )

        consumer = await create_consumer(form, mock_conn)
        assert consumer == mock_consumer

    @patch("internal.auth.creation.get_location")
    @patch("internal.auth.creation.SellerQuerier")
    @patch("internal.auth.creation.create_user")
    async def test_create_seller_success(  # noqa: PLR6301
        self,
        mock_create_user: MagicMock,
        mock_querier: MagicMock,
        mock_get_loc: MagicMock,
    ) -> None:
        """Test creating a seller and resolving its location."""
        mock_conn = MagicMock()

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_create_user.return_value = mock_user

        # Mock Geolocation
        mock_loc = MagicMock()
        mock_loc.lat = TEST_LAT
        mock_loc.lon = TEST_LON
        mock_get_loc.return_value = mock_loc

        mock_seller = MagicMock()
        mock_querier.return_value.create_seller = AsyncMock(return_value=mock_seller)

        form = CreateSellerForm(
            username="seller",
            email="s@test.com",
            password=SecretStr("pw"),
            seller_name="Bakery",
            address_line1="123 St",
            city="London",
            post_code="E1",
            country="UK",
            latitude=0,
            longitude=0,
        )

        seller = await create_seller(form, mock_conn)

        assert seller == mock_seller
        mock_get_loc.assert_called_once()

    @patch("internal.auth.creation.AdminQuerier")
    @patch("internal.auth.creation.create_user")
    async def test_create_admin_success(  # noqa: PLR6301
        self, mock_create_user: MagicMock, mock_querier: MagicMock
    ) -> None:
        """Test creating an admin and its base user."""
        mock_conn = MagicMock()

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_create_user.return_value = mock_user

        mock_admin = MagicMock()
        mock_querier.return_value.create_admin = AsyncMock(return_value=mock_admin)

        form = CreateAdminForm(
            username="madmin",
            email="madmin@amdin.com",
            password=SecretStr("pass"),
            first_name="Admin",
            last_name="BehzatC",
        )

        admin = await create_admin(form, mock_conn)
        assert admin == mock_admin
