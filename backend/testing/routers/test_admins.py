"""Tests for admin endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
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
    admin.username = "admin_"
    admin.email = "admin@testlock.com"
    admin.fname = "Admin"
    admin.lname = "Baskan"
    return admin


def get_mock_user() -> MagicMock:
    """Create a mocked user object.

    Returns:
        MagicMock: A mocked user object.
    """
    user = MagicMock()
    user.user_id = TEST_USER_ID
    user.username = "user"
    user.email = "user@test.com"
    user.role = "consumer"
    return user


def get_mock_consumer() -> MagicMock:
    """Create a mocked consumer object.

    Returns:
        MagicMock: A mocked consumer object.
    """
    consumer = MagicMock()
    consumer.user_id = TEST_USER_ID
    consumer.username = "consumer"
    consumer.email = "consumer@test.com"
    consumer.fname = "Con"
    consumer.lname = "Sumer"
    return consumer


def get_mock_seller() -> MagicMock:
    """Create a mocked seller object.

    Returns:
        MagicMock: A mocked seller object.
    """
    seller = MagicMock()
    seller.user_id = TEST_SELLER_ID
    seller.username = "satilmis"
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


def get_mock_bundle() -> MagicMock:
    """Create a mocked bundle object.

    Returns:
        MagicMock: A mocked bundle object.
    """
    bundle = MagicMock()
    bundle.bundle_id = 1
    bundle.seller_id = 1
    bundle.total_qty = 10
    bundle.bundle_name = "Bundle"
    bundle.description = "Desc"
    bundle.price = 10.0
    bundle.discount_percentage = 10
    bundle.window_start = datetime.now()  # noqa: DTZ005
    bundle.window_end = datetime.now()  # noqa: DTZ005
    return bundle


def get_mock_reservation() -> MagicMock:
    """Create a mocked reservation object.

    Returns:
        MagicMock: A mocked reservation object.
    """
    res = MagicMock()
    res.reservation_id = 1
    res.bundle_id = 1
    res.consumer_id = 1
    res.claim_code = "AA-BB"
    return res


def get_mock_allergen() -> MagicMock:
    """Create a mocked allergen object.

    Returns:
        MagicMock: A mocked allergen object.
    """
    al = MagicMock()
    al.allergen_id = 1
    al.allergen_name = "Nuts"
    return al


def get_mock_category() -> MagicMock:
    """Create a mocked category object.

    Returns:
        MagicMock: A mocked category object.
    """
    category = MagicMock()
    category.category_id = TEST_CATEGORY_ID
    category.category_name = "Pizza"
    category.category_coefficient = 1.5
    return category


def get_mock_badge() -> MagicMock:
    """Create a mocked badge object.

    Returns:
        MagicMock: A mocked badge object.
    """
    badge = MagicMock()
    badge.badge_id = 1
    badge.name = "Badge"
    badge.description = "Desc"
    return badge


def get_mock_admin_report() -> MagicMock:
    """Create a mocked admin report.

    Returns:
        MagicMock: A mocked admin report.
    """
    rep = MagicMock()
    rep.report_id = 1
    rep.user_id = 1
    rep.issue_type = "APP_CRASH"
    rep.description = "Desc"
    rep.status = "open"
    return rep


def get_mock_seller_report() -> MagicMock:
    """Create a mocked seller report.

    Returns:
        MagicMock: A mocked seller report.
    """
    rep = MagicMock()
    rep.report_id = 1
    rep.reservation_id = 1
    rep.issue_type = "ITEM_MISSING"
    rep.description = "Desc"
    rep.status = "open"
    return rep


def get_mock_inbox() -> MagicMock:
    """Create a mocked inbox message.

    Returns:
        MagicMock: A mocked inbox message.
    """
    inbox = MagicMock()
    inbox.message_id = TEST_MESSAGE_ID
    inbox.user_id = 1
    inbox.sender_id = 2
    inbox.message_subject = "Hello"
    inbox.message_text = "What's up!"
    return inbox


class TestAdmins(TestCase):  # noqa: PLR0904
    """Test suite for admin-related functionality."""

    def setUp(self) -> None:
        """Runs before every test to set up the client."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to tear down the client."""
        del self.client
        cleanup_database()

    @patch("routers.admins.create_admin")
    def test_register_admin(self, mock_create: MagicMock) -> None:
        """Test root user registering a new admin."""
        app.dependency_overrides[root_auth] = override_root_auth

        mock_create.side_effect = AsyncMock(return_value=None)

        payload = {
            "username": "gladio",
            "email": "capsizabidin@kv.com",
            "password": "securepass",
            "first_name": "New",
            "last_name": "Abidin",
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

        async def mock_generator(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_admin()

        mock_instance.get_admins.side_effect = mock_generator

        response = self.client.get("/admins")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH

        del app.dependency_overrides[root_auth]

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

        mock_user = MagicMock()
        mock_user.user_id = TEST_USER_ID
        mock_user.username = "deleted_user"
        mock_user.email = "deleted@test.com"
        mock_user.role = "consumer"

        mock_instance.delete_user = AsyncMock(return_value=mock_user)

        response = self.client.delete(f"/admins/database/users/{TEST_USER_ID}")

        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

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

    @patch("routers.admins.CategoryQuerier")
    def test_create_category(self, mock_querier: MagicMock) -> None:
        """Test admin creating a new category."""
        app.dependency_overrides[admin_auth] = override_admin_auth

        mock_instance = mock_querier.return_value
        mock_instance.create_category = AsyncMock(return_value=get_mock_category())

        payload = {"category_name": "Pizza", "category_coefficient": 1.5}

        response = self.client.post("/admins/database/categories", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["category_name"] == "Pizza"

        del app.dependency_overrides[admin_auth]

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
            "message_text": "What's up!",
        }

        response = self.client.post("/admins/database/inbox", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message_subject"] == "Hello"

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AdminQuerier")
    def test_get_admin_by_id(self, mock_querier: MagicMock) -> None:
        """Test getting admin by id via root auth."""
        app.dependency_overrides[root_auth] = override_root_auth
        mock_instance = mock_querier.return_value
        mock_instance.get_admin = AsyncMock(return_value=get_mock_admin())

        response = self.client.get(f"/admins/{TEST_ADMIN_ID}")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[root_auth]

    @patch("routers.admins.AdminQuerier")
    def test_update_admin(self, mock_querier: MagicMock) -> None:
        """Test updating admin profile."""
        app.dependency_overrides[root_auth] = override_root_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_admin = AsyncMock(return_value=get_mock_admin())

        payload = {"first_name": "Up", "last_name": "Date"}
        response = self.client.patch(f"/admins/{TEST_ADMIN_ID}", json=payload)

        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[root_auth]

    @patch("routers.admins.AdminQuerier")
    def test_deactivate_admin(self, mock_querier: MagicMock) -> None:
        """Test deactivating an admin."""
        app.dependency_overrides[root_auth] = override_root_auth
        mock_instance = mock_querier.return_value
        mock_instance.set_is_admin_active = AsyncMock(return_value=get_mock_admin())

        response = self.client.patch(f"/admins/{TEST_ADMIN_ID}/deactivate")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[root_auth]

    @patch("routers.admins.AdminQuerier")
    def test_activate_admin(self, mock_querier: MagicMock) -> None:
        """Test activating an admin."""
        app.dependency_overrides[root_auth] = override_root_auth
        mock_instance = mock_querier.return_value
        mock_instance.set_is_admin_active = AsyncMock(return_value=get_mock_admin())

        response = self.client.patch(f"/admins/{TEST_ADMIN_ID}/activate")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[root_auth]

    @patch("routers.admins.UserQuerier")
    def test_get_all_users(self, mock_querier: MagicMock) -> None:
        """Test getting all users as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_user()

        mock_instance.get_users.side_effect = mock_gen

        response = self.client.get("/admins/database/users")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.UserQuerier")
    def test_update_user_email(self, mock_querier: MagicMock) -> None:
        """Test updating user email as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        mock_row = MagicMock()
        mock_row.user_id = TEST_USER_ID
        mock_row.username = "user"
        mock_row.email = "new@test.com"
        mock_row.role = "consumer"
        mock_instance.update_user_email = AsyncMock(return_value=mock_row)

        payload = {"email": "new@test.com"}
        response = self.client.patch(
            f"/admins/database/users/{TEST_USER_ID}/email", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.hash_password")
    @patch("routers.admins.UserQuerier")
    def test_update_user_password(
        self, mock_querier: MagicMock, mock_hash: MagicMock
    ) -> None:
        """Test updating user password as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        mock_hash.return_value = "hashed"

        mock_row = MagicMock()
        mock_row.user_id = TEST_USER_ID
        mock_row.username = "user"
        mock_row.email = "test@test.com"
        mock_row.role = "consumer"
        mock_row.pw_hash = "hashed"
        mock_instance.update_user_password = AsyncMock(return_value=mock_row)

        payload = {"password": "newpassword"}
        response = self.client.patch(
            f"/admins/database/users/{TEST_USER_ID}/password", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerQuerier")
    def test_get_all_sellers(self, mock_querier: MagicMock) -> None:
        """Test getting all sellers as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_seller()

        mock_instance.get_sellers.side_effect = mock_gen

        response = self.client.get("/admins/database/sellers")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerQuerier")
    def test_unverify_seller(self, mock_querier: MagicMock) -> None:
        """Test unverifying a seller as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.unverify_seller = AsyncMock(return_value=get_mock_seller())

        response = self.client.patch(
            f"/admins/database/sellers/{TEST_SELLER_ID}/unverify"
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerQuerier")
    def test_update_seller_profile(self, mock_querier: MagicMock) -> None:
        """Test updating a seller profile as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        mock_seller = get_mock_seller()
        mock_instance.get_seller = AsyncMock(return_value=mock_seller)
        mock_instance.update_seller = AsyncMock(return_value=mock_seller)

        payload = {
            "seller_name": "Up",
            "address_line1": "Date",
            "city": "City",
            "post_code": "PC",
            "country": "Country",
            "latitude": 50.0,
            "longitude": 50.0,
        }
        response = self.client.patch(
            f"/admins/database/sellers/{TEST_SELLER_ID}", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.ConsumerQuerier")
    def test_get_all_consumers(self, mock_querier: MagicMock) -> None:
        """Test getting all consumers as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_consumer()

        mock_instance.get_consumers.side_effect = mock_gen

        response = self.client.get("/admins/database/consumers")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.ConsumerQuerier")
    def test_update_consumer_profile(self, mock_querier: MagicMock) -> None:
        """Test updating a consumer profile as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_consumer = AsyncMock(return_value=get_mock_consumer())

        payload = {"first_name": "Up", "last_name": "Date"}
        response = self.client.patch(
            f"/admins/database/consumers/{TEST_USER_ID}", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.BundleQuerier")
    def test_get_all_bundles(self, mock_querier: MagicMock) -> None:
        """Test getting all bundles as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        mock_instance.get_bundles.side_effect = mock_gen

        response = self.client.get("/admins/database/bundles")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.BundleQuerier")
    def test_delete_bundle(self, mock_querier: MagicMock) -> None:
        """Test deleting a bundle as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.delete_bundle = AsyncMock(return_value=get_mock_bundle())

        response = self.client.delete("/admins/database/bundles/1")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.ReservationsQuerier")
    def test_get_all_reservations(self, mock_querier: MagicMock) -> None:
        """Test getting all reservations as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        mock_instance.get_reservations.side_effect = mock_gen

        response = self.client.get("/admins/database/reservations")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.ReservationsQuerier")
    def test_delete_reservation(self, mock_querier: MagicMock) -> None:
        """Test deleting a reservation as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.delete_reservation = AsyncMock(
            return_value=get_mock_reservation()
        )

        response = self.client.delete("/admins/database/reservations/1")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AllergensQuerier")
    def test_get_all_allergens(self, mock_querier: MagicMock) -> None:
        """Test getting all allergens as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_allergen()

        mock_instance.get_allergens.side_effect = mock_gen

        response = self.client.get("/admins/database/allergens")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AllergensQuerier")
    def test_create_allergen(self, mock_querier: MagicMock) -> None:
        """Test creating an allergen as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.create_allergen = AsyncMock(return_value=get_mock_allergen())

        payload = {"allergen_name": "Nuts"}
        response = self.client.post("/admins/database/allergens", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AllergensQuerier")
    def test_update_allergen(self, mock_querier: MagicMock) -> None:
        """Test updating an allergen as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_allergen = AsyncMock(return_value=get_mock_allergen())

        payload = {"allergen_name": "Peanuts"}
        response = self.client.patch("/admins/database/allergens/1", json=payload)
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AllergensQuerier")
    def test_delete_allergen(self, mock_querier: MagicMock) -> None:
        """Test deleting an allergen as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.delete_allergen = AsyncMock(return_value=get_mock_allergen())

        response = self.client.delete("/admins/database/allergens/1")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.CategoryQuerier")
    def test_get_all_categories(self, mock_querier: MagicMock) -> None:
        """Test getting all categories as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_category()

        mock_instance.get_categories.side_effect = mock_gen

        response = self.client.get("/admins/database/categories")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.CategoryQuerier")
    def test_update_category(self, mock_querier: MagicMock) -> None:
        """Test updating a category as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_category = AsyncMock(return_value=get_mock_category())

        payload = {"category_name": "Burger", "category_coefficient": 1.2}
        response = self.client.patch("/admins/database/categories/1", json=payload)
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.CategoryQuerier")
    def test_delete_category(self, mock_querier: MagicMock) -> None:
        """Test deleting a category as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.delete_category = AsyncMock(return_value=get_mock_category())

        response = self.client.delete("/admins/database/categories/1")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.BadgeQuerier")
    def test_get_all_badges(self, mock_querier: MagicMock) -> None:
        """Test getting all badges as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_badge()

        mock_instance.get_badges.side_effect = mock_gen

        response = self.client.get("/admins/database/badges")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.BadgeQuerier")
    def test_update_badge(self, mock_querier: MagicMock) -> None:
        """Test updating a badge as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_badge = AsyncMock(return_value=get_mock_badge())

        payload = {"name": "New", "description": "New Desc"}
        response = self.client.patch("/admins/database/badges/1", json=payload)
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AdminIssueReportsQuerier")
    def test_get_admin_reports(self, mock_querier: MagicMock) -> None:
        """Test getting all admin issue reports."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_admin_report()

        mock_instance.get_admin_issue_reports.side_effect = mock_gen

        response = self.client.get("/admins/database/reports/admin")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.AdminIssueReportsQuerier")
    def test_update_admin_report_status(self, mock_querier: MagicMock) -> None:
        """Test updating an admin report status."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_admin_issue_report_status = AsyncMock(
            return_value=get_mock_admin_report()
        )

        payload = {"status": "closed"}
        response = self.client.patch(
            "/admins/database/reports/admin/1/status", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerIssueReportsQuerier")
    def test_get_seller_reports(self, mock_querier: MagicMock) -> None:
        """Test getting all seller issue reports."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_seller_report()

        mock_instance.get_seller_issue_reports.side_effect = mock_gen

        response = self.client.get("/admins/database/reports/seller")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.SellerIssueReportsQuerier")
    def test_update_seller_report_status(self, mock_querier: MagicMock) -> None:
        """Test updating a seller report status."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.update_seller_issue_report_status = AsyncMock(
            return_value=get_mock_seller_report()
        )

        payload = {"status": "closed"}
        response = self.client.patch(
            "/admins/database/reports/seller/1/status", json=payload
        )
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.InboxQuerier")
    def test_get_all_inboxes(self, mock_querier: MagicMock) -> None:
        """Test getting all inbox messages."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_inbox()

        mock_instance.get_inboxes.side_effect = mock_gen

        response = self.client.get("/admins/database/inbox")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.InboxQuerier")
    def test_get_user_inbox(self, mock_querier: MagicMock) -> None:
        """Test getting a user's inbox as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value

        async def mock_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_inbox()

        mock_instance.get_user_inbox.side_effect = mock_gen

        response = self.client.get(f"/admins/database/inbox/user/{TEST_USER_ID}")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]

    @patch("routers.admins.InboxQuerier")
    def test_delete_inbox_message(self, mock_querier: MagicMock) -> None:
        """Test deleting an inbox message as admin."""
        app.dependency_overrides[admin_auth] = override_admin_auth
        mock_instance = mock_querier.return_value
        mock_instance.delete_inbox_message = AsyncMock(return_value=get_mock_inbox())

        response = self.client.delete("/admins/database/inbox/1")
        assert response.status_code == status.HTTP_200_OK

        del app.dependency_overrides[admin_auth]
