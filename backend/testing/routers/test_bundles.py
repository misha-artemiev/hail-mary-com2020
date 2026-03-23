"""Tests for bundle endpoints."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from internal.auth.middleware import consumer_auth
from main import app
from testing.test_database import cleanup_database, init_database

# Constants
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


class MockModel:
    """Mock database row models to satisfy FastAPI response validation."""

    def __init__(self, **kwargs: Any) -> None:  # noqa: D107, ANN401
        self.bundle_id = TEST_BUNDLE_ID
        self.seller_id = TEST_SELLER_ID
        self.consumer_id = TEST_USER_ID
        self.reservation_id = TEST_RESERVATION_ID
        self.bundle_name = "Test Bundle"
        self.sellers_name = "Test Seller"
        self.seller_name = "Test Seller"
        self.description = "Test Description"
        self.bundle_description = "Test Description"
        self.price = TEST_PRICE
        self.discount_percentage = int(TEST_DISCOUNT)
        self.total_qty = TEST_QTY
        self.window_start = datetime.now(tz=UTC)
        self.window_end = datetime.now(tz=UTC)
        self.carbon_dioxide = 10
        self.reserved_at = datetime.now(tz=UTC)
        self.created_at = datetime.now(tz=UTC)
        self.claim_code = "ABCDE"
        self.collected_at = None
        self.dist = 5.0

        self.bundle_category: list[int] = []
        self.bundle_allergens: list[int] = []

        self.__dict__.update(kwargs)


def override_consumer_auth() -> MagicMock:
    """Mock consumer auth.

    Returns:
        MagicMock: Mock object with user_id and role.
    """
    mock = MagicMock()
    mock.user_id = TEST_USER_ID
    mock.role = "consumer"
    return mock


def get_mock_bundle(qty: int = TEST_QTY) -> MockModel:
    """Mock bundle helper.

    Returns:
        MockModel: Mock bundle with specified quantity.
    """
    return MockModel(total_qty=qty)


def get_mock_seller() -> MockModel:
    """Mock seller helper.

    Returns:
        MockModel: Mock seller with test data.
    """
    return MockModel(
        seller_id=TEST_SELLER_ID,
        user_id=1,
        seller_name="Bakery",
        latitude=TEST_LAT,
        longitude=TEST_LON,
    )


def get_mock_reservation() -> MockModel:
    """Mock reservation helper.

    Returns:
        MockModel: Mock reservation with test data.
    """
    return MockModel(reservation_id=TEST_RESERVATION_ID)


class TestBundles(TestCase):
    """Test suite."""

    def setUp(self) -> None:  # noqa: D102
        init_database()
        self.client = TestClient(app)
        app.dependency_overrides[consumer_auth] = override_consumer_auth

    def tearDown(self) -> None:  # noqa: D102
        del self.client
        cleanup_database()
        app.dependency_overrides.clear()

    @patch("routers.bundles.BundleQuerier")
    def test_get_bundles_success(self, mock_querier: MagicMock) -> None:
        """Test getting bundles list."""

        async def mock_generator(
            *args: object, **kwargs: object
        ) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        mock_querier.return_value.get_bundles.side_effect = mock_generator
        response = self.client.get("/bundles/")
        assert response.status_code == status.HTTP_200_OK

    @patch("routers.bundles.get_distance")
    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.CategoriesQuerier")
    @patch("routers.bundles.AllergensQuerier")
    @patch("routers.bundles.BundleQuerier")
    @patch("routers.bundles.SellerQuerier")
    def test_search_bundles_success(  # noqa: PLR0913, PLR0917
        self,
        mock_seller_inst: MagicMock,
        mock_bundle_inst: MagicMock,
        mock_allergens_inst: MagicMock,
        mock_categories_inst: MagicMock,
        mock_res_inst: MagicMock,
        mock_dist: MagicMock,
    ) -> None:
        """Test searching for bundles."""
        mock_dist.return_value = 5.0

        async def make_iter(items: list[Any]) -> AsyncGenerator[Any]:  # noqa: RUF029
            for item in items:
                yield item

        async def seller_loc_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_seller()

        async def bundle_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_bundle()

        async def empty_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            return
            yield  # type: ignore[unreachable]

        async def single_res_gen(*_: object, **__: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        mock_seller_inst.return_value.get_seller_by_location.side_effect = (
            seller_loc_gen
        )
        mock_bundle_inst.return_value.get_sellers_active_bundles.side_effect = (
            bundle_gen
        )
        mock_allergens_inst.return_value.get_bundle_allergens.side_effect = empty_gen
        mock_categories_inst.return_value.get_bundle_categories.side_effect = empty_gen
        mock_res_inst.return_value.get_bundle_reservations.side_effect = single_res_gen
        mock_seller_inst.return_value.get_seller = AsyncMock(
            return_value=get_mock_seller()
        )

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

    @patch("routers.bundles.block_management")
    @patch("routers.bundles.BundleQuerier")
    def test_get_bundle_image(
        self, mock_querier: MagicMock, mock_bm: MagicMock
    ) -> None:
        """Test fetching image."""
        mock_querier.return_value.get_bundle = AsyncMock(return_value=get_mock_bundle())
        mock_bm.get_bundle_image.return_value = b"image_data"
        response = self.client.get("/bundles/1/image")
        assert response.status_code == status.HTTP_200_OK

    @patch("routers.bundles.BundleQuerier")
    def test_get_bundle_image_not_found(self, mock_querier: MagicMock) -> None:
        """Test missing image."""
        mock_querier.return_value.get_bundle = AsyncMock(return_value=None)
        response = self.client.get("/bundles/1/image")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("routers.bundles.generate_claim_code")
    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.BundleQuerier")
    def test_create_reservation_success(
        self,
        mock_bundle_querier: MagicMock,
        mock_res_querier: MagicMock,
        mock_gen_code: MagicMock,
    ) -> None:
        """Test successful reservation."""
        mock_bundle_querier.return_value.get_bundle_lock = AsyncMock(
            return_value=get_mock_bundle()
        )

        async def empty_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            items: list[Any] = []
            for item in items:
                yield item

        mock_res_inst = mock_res_querier.return_value
        mock_res_inst.get_bundle_reservations.side_effect = empty_gen
        mock_res_inst.create_reservation = AsyncMock(
            return_value=get_mock_reservation()
        )
        mock_res_inst.get_consumer_reservation = AsyncMock(return_value=[])
        mock_gen_code.return_value = "AAAAA"

        response = self.client.post("/bundles/1/reservations")
        assert response.status_code == status.HTTP_201_CREATED

    @patch("routers.bundles.ReservationQuerier")
    @patch("routers.bundles.BundleQuerier")
    def test_create_reservation_bundle_full(
        self, mock_bundle_querier: MagicMock, mock_res_querier: MagicMock
    ) -> None:
        """Test full bundle reservation fails."""
        mock_bundle_querier.return_value.get_bundle_lock = AsyncMock(
            return_value=get_mock_bundle(qty=TEST_QTY_FULL)
        )

        async def full_res_gen(*args: object, **kwargs: object) -> AsyncGenerator[Any]:
            await asyncio.sleep(0)
            yield get_mock_reservation()

        mock_res_querier.return_value.get_bundle_reservations.side_effect = full_res_gen
        response = self.client.post("/bundles/1/reservations")
        assert response.status_code == status.HTTP_409_CONFLICT
