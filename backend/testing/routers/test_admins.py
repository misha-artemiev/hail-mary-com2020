"""Tests for admin endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import admin_auth, root_auth
from main import app
from testing.test_database import cleanup_database, init_database

# Constants
TEST_ADMIN_ID = 99
TEST_USER_ID = 5
TEST_SELLER_ID = 10
TEST_CATEGORY_ID = 1
TEST_MESSAGE_ID = 1
TEST_LAT = 50.0
TEST_LON = -0.5
EXPECTED_LIST_LENGTH = 1


def override_root_auth() -> None:
    """Mock the root authentication dependency."""
    return


def override_admin_auth() -> MagicMock:
    """Mock the admin authentication dependency.

    Returns:
        MagicMock: Mock Object simulator for an admin session.
    """
    mock = MagicMock()
    mock.user_id = TEST_ADMIN_ID
    mock.role = "admin"
    return mock


def get_mock_admin() -> MagicMock:
    """Create a mocked admin object.

    Returns:
        MagicMock: A mocked admin object.
    """
    admin = MagicMock()
    admin.user_id = TEST_ADMIN_ID
    admin.username = "admin_user"
    admin.email = "admin@test.com"
    admin.fname = "Admin"
    admin.lname = "User"
    return admin


def get_mock_seller() -> MagicMock:
    """Create a mocked seller object.

    Returns:
        MagicMock: A mocked seller object.
    """
    seller = MagicMock()
    seller.user_id = TEST_SELLER_ID
    seller.username = "seller_user"
    seller.email = "seller@test.com"
    seller.seller_name = "Mock Seller"
    seller.address_line1 = "123 Mock St"
    seller.address_line2 = "Apt 1"
    seller.city = "London"
    seller.post_code = "E1"
    seller.region = "Greater London"
    seller.country = "UK"
    seller.verified_by = None
    seller.latitude = TEST_LAT
    seller.longitude = TEST_LON
    return seller


def get_mock_category() -> MagicMock:
    """Create a mocked category object.

    Returns:
        MagicMock: A mocked category object.
    """
    category = MagicMock()
    category.category_id = TEST_CATEGORY_ID
    category.category_name = "Test Category"
    category.category_coefficient = 1.5
    return category


def get_mock_inbox() -> MagicMock:
    """Create a mocked inbox message.

    Returns:
        MagicMock: A mocked inbox message.
    """
    inbox = MagicMock()
    inbox.message_id = TEST_MESSAGE_ID
    inbox.message_subject = "Hello"
    inbox.message_text = "World"
    return inbox


class TestAdmins(TestCase):
    """Test suite for admin-related functionality."""

    def setUp(self) -> None:
        """Runs before every test to set up the client."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to tear down the client."""
        del self.client
        cleanup_database()

    # --- ROOT AUTH ENDPOINTS ---

    @patch("routers.admins.create_admin")
    def test_register_admin(self, mock_create: MagicMock) -> None:
        """Test root user registering a new admin."""
        app.dependency_overrides[root_auth] = override_root_auth

        mock_create.side_effect = AsyncMock(return_value=None)

        payload = {
            "username": "new_admin",
            "email": "admin@test.com",
            "password": "securepass",
            "first_name": "New",
            "last_name": "Admin",
        }

        response = self.client.post("/admins", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        mock_create.assert_called_once()

        del app.dependency_overrides[root_auth]

    @patch("routers.admins.AdminQuerier")
    def test_get_admins(self, mock_querier: MagicMock) -> None:
        """Test getting all admins via root auth."""
        app.dependency_overrides[root_auth] = override_root_auth

        mock_instance = mock_querier.return_value

        async def mock_generator(
            *_: object, **__: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_admin()

        mock_instance.get_admins.side_effect = mock_generator

        response = self.client.get("/admins")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH

        del app.dependency_overrides[root_auth]

    # --- ADMIN AUTH ENDPOINTS ---

    @patch("routers.admins.AdminQuerier")
    def test_get_admin_me(self, mock_querier: MagicMock) -> None:
        """Test getting authenticated admin profile."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value
        mock_instance.get_admin = AsyncMock(return_value=get_mock_admin())

        response = self.client.get("/admins/me")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["fname"] == "Admin"

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.UserQuerier")
    def test_delete_user(self, mock_querier: MagicMock) -> None:
        """Test admin deleting a user."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value

        # Add required Pydantic fields to the deleted user mock
        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.username = "deleted_user"
        mock_user.email = "deleted@test.com"
        mock_user.role = "consumer"  # Must explicitly match the Enum strings

        mock_instance.delete_user = AsyncMock(return_value=mock_user)

        response = self.client.delete(f"/admins/database/users/{TEST_USER_ID}")

        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    # --- SELLER VERIFICATION BUSINESS LOGIC ---

    @patch("routers.admins.SellerQuerier")
    def test_verify_seller_success(self, mock_querier: MagicMock) -> None:
        """Test successfully verifying a seller with coordinates."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value
        mock_instance.get_seller = AsyncMock(return_value=get_mock_seller())
        mock_instance.verify_seller = AsyncMock(return_value=get_mock_seller())

        response = self.client.patch(
            f"/admins/database/sellers/{TEST_SELLER_ID}/verify"
        )

        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerQuerier")
    def test_verify_seller_no_coords(self, mock_querier: MagicMock) -> None:
        """Test failure when verifying a seller without coordinates."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value

        # Seller missing coordinates
        mock_seller = get_mock_seller()
        mock_seller.latitude = None
        mock_seller.longitude = None
        mock_instance.get_seller = AsyncMock(return_value=mock_seller)

        response = self.client.patch(
            f"/admins/database/sellers/{TEST_SELLER_ID}/verify"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "valid coordinates" in response.json()["detail"]

        del app.dependency_overrides[admin_auth]

    # --- CATEGORY CRUD ---

    @patch("routers.admins.CategoryQuerier")
    def test_create_category(self, mock_querier: MagicMock) -> None:
        """Test admin creating a new category."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value
        mock_instance.create_category = AsyncMock(return_value=get_mock_category())

        payload = {
            "category_name": "Test Category",
            "category_coefficient": 1.5,
        }

        response = self.client.post("/admins/database/categories", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["category_name"] == "Test Category"

        del app.dependency_overrides[admin_auth]

    # --- INBOX MESSAGES ---

    @patch("routers.admins.InboxQuerier")
    def test_create_inbox_message(self, mock_querier: MagicMock) -> None:
        """Test admin creating an inbox message."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value
        mock_instance.create_inbox_message = AsyncMock(return_value=get_mock_inbox())

        payload = {
            "user_id": TEST_USER_ID,
            "sender_id": TEST_ADMIN_ID,
            "message_subject": "Hello",
            "message_text": "World",
        }

        response = self.client.post("/admins/database/inbox", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message_subject"] == "Hello"

        del app.dependency_overrides[admin_auth]
