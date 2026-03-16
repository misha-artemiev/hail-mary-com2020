"""Tests for distance calculation modules."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from internal.geolocation.distance import dist_safe_box, get_distance
from internal.geolocation.types import LocationModel

# Constants
TEST_LAT = 51.5074
TEST_LON = -0.1278
TEST_DIST_KM = 10


class TestDistance(TestCase):
    """Test suite for geolocation distances."""

    @patch("internal.geolocation.distance.geodesic")
    def test_dist_safe_box(self, mock_geodesic: MagicMock) -> None:  # noqa: PLR6301
        """Test calculating the safe box borders."""
        mock_dest = MagicMock()
        mock_dest.destination.return_value = MagicMock(
            latitude=TEST_LAT, longitude=TEST_LON
        )
        mock_geodesic.return_value = mock_dest

        loc = LocationModel(lat=TEST_LAT, lon=TEST_LON)

        box = dist_safe_box(loc, TEST_DIST_KM)

        assert box.lat_max == TEST_LAT
        assert box.lat_min == TEST_LAT
        assert box.lon_max == TEST_LON
        assert box.lon_min == TEST_LON

    def test_get_distance_success(self) -> None:  # noqa: PLR6301
        """Test calculating the distance between two points successfully."""
        loc1 = LocationModel(lat=TEST_LAT, lon=TEST_LON)
        loc2 = LocationModel(lat=TEST_LAT + 1, lon=TEST_LON + 1)

        distance = get_distance(loc1, loc2)

        assert isinstance(distance, float)
        assert distance > 0.0

    @patch("internal.geolocation.distance.geodesic")
    def test_get_distance_failure(self, mock_geodesic: MagicMock) -> None:
        """Test calculating distance failure throws ValueError."""
        # Return a standard MagicMock that fails the 'is type geodesic' check
        mock_geodesic.return_value = MagicMock()

        loc1 = LocationModel(lat=TEST_LAT, lon=TEST_LON)
        loc2 = LocationModel(lat=TEST_LAT, lon=TEST_LON)

        with self.assertRaises(ValueError) as context:
            get_distance(loc1, loc2)

        assert "failed to calculate distance" in str(context.exception)
