"""Tests for seller endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import seller_auth
from internal.badges.engine import BadgeEngine
from main import app
from testing.routers.test_bundles import TEST_LAT, TEST_LON
from testing.test_database import cleanup_database, init_database

# Constants to satisfy magic number linter
TEST_SELLER_ID = 10
TEST_USER_ID = 10
TEST_BUNDLE_ID = 1
TEST_RESERVATION_ID = 100
TEST_QTY = 10
TEST_PRICE = 10.0
TEST_DISCOUNT = 50
EXPECTED_LIST_LENGTH = 1


def override_seller_auth() -> MagicMock:
    """Mock the seller authentication dependency.

    Returns:
        MagicMock: Mock Object simulator.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    mock.role = "seller"
    return mock


def override_badge_engine() -> MagicMock:
    """Mock the badge engine dependency.

    Returns:
        MagicMock: Mock Object simulator for the badge engine.
    """
    mock = MagicMock()
    mock.run = MagicMock()
    return mock


def get_mock_seller() -> MagicMock:
    """Create a mocked seller object.

    Returns:
        MagicMock: A mocked seller object.
    """
    seller = MagicMock()
    seller.user_id = TEST_SELLER_ID
    seller.seller_name = "Mycroft Holmes"
    seller.latitude = TEST_LAT
    seller.longitude = TEST_LON

    # Add these fields to prevent FastAPI validation errors
    seller.username = "I love Sherlock"
    seller.email = "sherlock@holmes.com"
    seller.address_line1 = "221B Baker St"
    seller.address_line2 = "Apt 2"
    seller.city = "London"
    seller.post_code = "NW1 6XE"
    seller.region = "Greater London"
    seller.country = "United Kingdom"

    return seller


def get_mock_bundle() -> MagicMock:
    """Create a mocked bundle object.

    Returns:
        MagicMock: A mocked bundle object.
    """
    bundle = MagicMock()
    bundle.bundle_id = TEST_BUNDLE_ID
    bundle.seller_id = TEST_SELLER_ID
    bundle.total_qty = TEST_QTY
    bundle.bundle_name = "Test Bundle"
    bundle.description = "Test Desc"
    bundle.price = TEST_PRICE
    bundle.discount_percentage = TEST_DISCOUNT
    bundle.window_start = datetime.now()  # noqa: DTZ005
    bundle.window_end = datetime.now()  # noqa: DTZ005
    return bundle


def get_mock_reservation() -> MagicMock:
    """Create a mocked reservation object.

    Returns:
        MagicMock: A mocked reservation object.
    """
    res = MagicMock()
    res.reservation_id = TEST_RESERVATION_ID
    res.bundle_id = TEST_BUNDLE_ID
    res.consumer_id = 99
    res.claim_code = "AA11AA"
    return res


class TestSellers(TestCase):
    """Test suite for seller-related functionality."""

    def setUp(self) -> None:
        """Runs before every test to set up the client."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to tear down the client."""
        del self.client
        cleanup_database()

    @patch("routers.sellers.SellerQuerier")
    def test_get_sellers(self, mock_querier: MagicMock) -> None:
        """Test getting a list of all sellers."""
        mock_instance = mock_querier.return_value

        async def mock_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_seller()

        mock_instance.get_sellers.side_effect = mock_generator

        response = self.client.get("/sellers")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH
        assert response.json()[0]["seller_name"] == "Mycroft Holmes"

    @patch("routers.sellers.SellerQuerier")
    def test_get_seller_me(self, mock_querier: MagicMock) -> None:
        """Test getting the authenticated seller profile."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_instance = mock_querier.return_value
        mock_instance.get_seller = AsyncMock(return_value=get_mock_seller())

        response = self.client.get("/sellers/me")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["seller_name"] == "Mycroft Holmes"

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.SellerQuerier")
    def test_get_seller_me_not_found(self, mock_querier: MagicMock) -> None:
        """Test getting authenticated seller profile when it doesn't exist."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_instance = mock_querier.return_value
        mock_instance.get_seller = AsyncMock(return_value=None)

        response = self.client.get("/sellers/me")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.SellerQuerier")
    def test_get_seller_by_id(self, mock_querier: MagicMock) -> None:
        """Test getting a seller by their specific ID."""
        mock_instance = mock_querier.return_value
        mock_instance.get_seller = AsyncMock(return_value=get_mock_seller())

        response = self.client.get(f"/sellers/{TEST_SELLER_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["seller_name"] == "Mycroft Holmes"

    @patch("routers.sellers.create_seller")
    def test_register_seller(self, mock_create: MagicMock) -> None:
        """Test registering a new seller."""
        mock_create.side_effect = AsyncMock(return_value=None)

        payload = {
            "username": "seller_test",
            "email": "seller@test.com",
            "password": "securepass",
            "first_name": "John",
            "last_name": "Doe",
            "seller_name": "Bakery Test",
            "latitude": 50.0,
            "longitude": 50.0,
            "address_line1": "123 Baker St",
            "address_line2": "Apt 2",
            "city": "London",
            "post_code": "NW1 6XE",
            "region": "Greater London",
            "country": "United Kingdom",
        }

        response = self.client.post("/sellers", json=payload)

        # This will print the exact missing field to your console if it fails again!
        if response.status_code != status.HTTP_201_CREATED:
            print("FASTAPI VALIDATION ERROR:", response.json())

        assert response.status_code == status.HTTP_201_CREATED
        mock_create.assert_called_once()

    @patch("routers.sellers.BundleQuerier")
    def test_create_bundle(self, mock_querier: MagicMock) -> None:
        """Test creating a bundle for the authenticated seller."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_instance = mock_querier.return_value
        mock_instance.create_bundle = AsyncMock(return_value=get_mock_bundle())

        payload = {
            "bundle_name": "Test Bundle",
            "description": "A nice bundle",
            "total_qty": TEST_QTY,
            "price": TEST_PRICE,
            "discount_percentage": TEST_DISCOUNT,
            "window_start": "2024-01-01T10:00:00",
            "window_end": "2024-01-01T12:00:00",
            "carbon_dioxide": 10000,
        }

        response = self.client.post("/sellers/me/bundles", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["bundle_name"] == "Test Bundle"

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.BundleQuerier")
    def test_update_bundle(self, mock_querier: MagicMock) -> None:
        """Test updating an existing bundle."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_instance = mock_querier.return_value
        mock_instance.update_bundle = AsyncMock(return_value=get_mock_bundle())

        payload = {
            "bundle_name": "Updated Bundle",
            "description": "Updated nice bundle",
            "total_qty": TEST_QTY,
            "price": TEST_PRICE,
            "discount_percentage": TEST_DISCOUNT,
            "window_start": "2024-01-01T10:00:00",
            "window_end": "2024-01-01T12:00:00",
            "carbon_dioxide": 10000,
        }

        response = self.client.patch(
            f"/sellers/me/bundles/{TEST_BUNDLE_ID}", json=payload
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["bundle_name"] == "Test Bundle"

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.BundleQuerier")
    def test_get_sellers_bundles(self, mock_querier: MagicMock) -> None:
        """Test getting all bundles owned by the seller."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_instance = mock_querier.return_value

        async def mock_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        mock_instance.get_sellers_bundles.side_effect = mock_generator

        response = self.client.get("/sellers/me/bundles")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.ReservationsQuerier")
    @patch("routers.sellers.BundleQuerier")
    def test_get_bundle_reservations(
        self, mock_bundle_querier: MagicMock, mock_res_querier: MagicMock
    ) -> None:
        """Test getting reservations for a specific seller's bundle."""
        app.dependency_overrides[seller_auth] = override_seller_auth

        mock_bundle_inst = mock_bundle_querier.return_value
        mock_bundle_inst.get_sellers_bundle = AsyncMock(return_value=get_mock_bundle())

        mock_res_inst = mock_res_querier.return_value

        async def mock_res_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        mock_res_inst.get_bundle_reservations.side_effect = mock_res_generator

        response = self.client.get(f"/sellers/me/bundles/{TEST_BUNDLE_ID}/reservations")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH
        assert response.json()[0]["reservation_id"] == TEST_RESERVATION_ID

        del app.dependency_overrides[seller_auth]

    @patch("routers.sellers.ReservationsQuerier")
    @patch("routers.sellers.BundleQuerier")
    def test_reservation_collection_success(
        self, mock_bundle_querier: MagicMock, mock_res_querier: MagicMock
    ) -> None:
        """Test confirming the collection of a reservation."""
        app.dependency_overrides[seller_auth] = override_seller_auth
        app.dependency_overrides[BadgeEngine] = override_badge_engine

        # Mock finding the reservation
        mock_res_inst = mock_res_querier.return_value
        mock_res_inst.get_reservation_collection = AsyncMock(
            return_value=get_mock_reservation()
        )

        # Mock validating the bundle ownership
        mock_bundle_inst = mock_bundle_querier.return_value
        mock_bundle_inst.get_bundle = AsyncMock(return_value=get_mock_bundle())

        # Mock the successful collection
        mock_res_inst.collect_reservation = AsyncMock(
            return_value=get_mock_reservation()
        )

        response = self.client.patch(
            f"/sellers/me/bundles/{TEST_BUNDLE_ID}/reservations/collect?claim_code=AAAA"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["reservation_id"] == TEST_RESERVATION_ID

        del app.dependency_overrides[seller_auth]
        del app.dependency_overrides[BadgeEngine]
