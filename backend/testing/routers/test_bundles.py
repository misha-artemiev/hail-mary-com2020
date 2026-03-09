"""Tests for bundle endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import consumer_auth
from main import app
from testing.test_database import cleanup_database, init_database

# Constants to satisfy magic number linter (ruff stuff)
TEST_BUNDLE_ID = 1
TEST_SELLER_ID = 5
TEST_USER_ID = 20
TEST_QTY = 10
TEST_QTY_FULL = 1
TEST_RESERVATION_ID = 100
EXPECTED_LIST_LENGTH = 1
TEST_LAT = 50.0
TEST_LON = 50.0
TEST_MAX_DIST = 10
TEST_PRICE = 10.0
TEST_DISCOUNT = 50


def override_consumer_auth() -> MagicMock:
    """Mock the consumer authentication dependency.

    Returns:
        MagicMock: Mock Object maker.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    mock.role = "consumer"
    return mock


def get_mock_bundle(qty: int = TEST_QTY) -> MagicMock:
    """Create a mocked bundle object.

    Args:
        qty: Total quantity of the bundle.

    Returns:
        MagicMock: A mocked bundle object.
    """
    bundle = MagicMock()
    bundle.bundle_id = TEST_BUNDLE_ID
    bundle.seller_id = TEST_SELLER_ID
    bundle.total_qty = qty
    bundle.bundle_name = "Test Bundle"
    bundle.description = "Test Descr"
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
    res.claim_code = "AA11AA"
    return res


def get_mock_seller() -> MagicMock:
    """Create a mocked seller object.

    Returns:
        MagicMock: A mocked seller object.
    """
    seller = MagicMock()
    seller.user_id = TEST_SELLER_ID
    seller.seller_name = "Test Seller"
    seller.latitude = TEST_LAT
    seller.longitude = TEST_LON
    return seller


class TestBundles(TestCase):
    """Test suite for bundle."""

    def setUp(self) -> None:
        """Runs before every test to set up the Testclient."""
        init_database()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Runs after every test to clean the Testclient."""
        del self.client
        cleanup_database()

    @patch("routers.bundles.BundleQuerier")
    def test_get_bundles_success(self, mock_querier: MagicMock) -> None:
        """Test getting a list of available bundles."""
        mock_instance = mock_querier.return_value

        async def mock_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        mock_instance.get_bundles.side_effect = mock_generator

        response = self.client.get("/bundles/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH
        assert response.json()[0]["bundle_name"] == "Test Bundle"

    @patch("routers.bundles.BundleQuerier")
    def test_get_bundle(self, mock_querier: MagicMock) -> None:
        """Test getting a single bundle by ID."""
        mock_instance = mock_querier.return_value
        mock_instance.get_bundle = AsyncMock(return_value=get_mock_bundle())

        response = self.client.get(f"/bundles/{TEST_BUNDLE_ID}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["bundle_id"] == TEST_BUNDLE_ID

    @patch("routers.bundles.BundleQuerier")
    def test_get_bundle_not_found(self, mock_querier: MagicMock) -> None:
        """Test getting a bundle that does not exist."""
        mock_instance = mock_querier.return_value
        mock_instance.get_bundle = AsyncMock(return_value=None)

        response = self.client.get(f"/bundles/{TEST_BUNDLE_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.BundleQuerier")
    def test_reserve_bundle_success(
        self, mock_bundle_querier: MagicMock, mock_res_querier: MagicMock
    ) -> None:
        """Test successfully reserving a bundle."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_bundle_inst = mock_bundle_querier.return_value
        mock_res_inst = mock_res_querier.return_value

        mock_bundle_inst.get_bundle_lock = AsyncMock(return_value=get_mock_bundle())

        async def mock_empty_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_res_inst.get_bundle_reservations.side_effect = mock_empty_generator
        mock_res_inst.create_reservation = AsyncMock(
            return_value=get_mock_reservation()
        )

        response = self.client.post(f"/bundles/{TEST_BUNDLE_ID}/reservations")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["reservation_id"] == TEST_RESERVATION_ID

        del app.dependency_overrides[consumer_auth]

    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.BundleQuerier")
    def test_reserve_bundle_sold_out(
        self, mock_bundle_querier: MagicMock, mock_res_querier: MagicMock
    ) -> None:
        """Test reserving a bundle that is already sold out."""
        app.dependency_overrides[consumer_auth] = override_consumer_auth

        mock_bundle_inst = mock_bundle_querier.return_value
        mock_res_inst = mock_res_querier.return_value

        # Setup: Bundle has qty of 1, but 1 reservation already exists
        mock_bundle_inst.get_bundle_lock = AsyncMock(
            return_value=get_mock_bundle(qty=TEST_QTY_FULL)
        )

        async def mock_res_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        mock_res_inst.get_bundle_reservations.side_effect = mock_res_generator

        response = self.client.post(f"/bundles/{TEST_BUNDLE_ID}/reservations")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "reservations available" in response.json()["detail"].lower()

        del app.dependency_overrides[consumer_auth]

    @patch("routers.bundles.get_distance")
    @patch("routers.bundles.dist_safe_box")
    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.CategoriesQuerier")
    @patch("routers.bundles.AllergensQuerier")
    @patch("routers.bundles.BundleQuerier")
    @patch("routers.bundles.SellerQuerier")
    def test_search_bundles_success(  # noqa: PLR0913, PLR0917
        self,
        mock_seller_querier: MagicMock,
        mock_bundle_querier: MagicMock,
        mock_allergens_querier: MagicMock,
        mock_categories_querier: MagicMock,
        mock_res_querier: MagicMock,
        mock_dist_box: MagicMock,
        mock_get_distance: MagicMock,
    ) -> None:
        """Test searching for bundles with criteria."""
        # Mock Location dependencies to bypass complex math
        mock_dist_box.return_value = MagicMock(
            lat_max=TEST_LAT, lat_min=TEST_LAT, lon_max=TEST_LON, lon_min=TEST_LON
        )
        mock_get_distance.return_value = 1.0

        # Setup Mock Instances
        mock_seller_inst = mock_seller_querier.return_value
        mock_bundle_inst = mock_bundle_querier.return_value
        mock_allergens_inst = mock_allergens_querier.return_value
        mock_categories_inst = mock_categories_querier.return_value
        mock_res_inst = mock_res_querier.return_value

        async def seller_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_seller()

        async def bundle_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        async def empty_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        async def res_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        # Attach generators to mocks
        mock_seller_inst.get_seller_by_location.side_effect = seller_gen
        mock_bundle_inst.get_sellers_active_bundles.side_effect = bundle_gen
        mock_allergens_inst.get_bundle_allergens.side_effect = empty_gen
        mock_categories_inst.get_bundle_categories.side_effect = empty_gen
        mock_res_inst.get_bundle_reservations.side_effect = res_gen

        payload = {
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "max_dist": TEST_MAX_DIST,
            "max_price": None,
            "seller_name": None,
            "allergens": None,
            "categories": None,
        }

        response = self.client.post("/bundles/search", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == EXPECTED_LIST_LENGTH
        assert response.json()[0]["bundle_name"] == "Test Bundle"
