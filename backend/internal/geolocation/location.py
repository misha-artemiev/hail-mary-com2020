"""Location translation."""

from geopy import Location  # type: ignore[import-untyped]
from geopy.geocoders import Nominatim  # type: ignore[import-untyped]

from .types import LocationModel


def get_location(address: str) -> LocationModel:
    """Coordinates from Address.

    Args:
      address: real address

    Returns:
      coordinates of the address (None, None if failed)
    """
    try:
        nom = Nominatim(user_agent="hail mary", timeout=10)
        loc = nom.geocode(address)
        if not loc or type(loc) is not Location:
            return LocationModel(lat=None, lon=None)
        return LocationModel(lat=loc.latitude, lon=loc.longitude)
    except Exception:
        return LocationModel(lat=None, lon=None)
