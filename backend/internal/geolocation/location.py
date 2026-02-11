"""Location translation."""

from geopy import Location  # type: ignore[import-untyped]
from geopy.geocoders import Nominatim  # type: ignore[import-untyped]

from .types import LocationModel


def get_location(address: str) -> LocationModel:
    """Coordinates from Address.

    Args:
      address: real address

    Returns:
      coordinates of the address

    Raises:
      ValueError: if failed to get location
    """
    nom = Nominatim(user_agent="hail mary", timeout=10)
    loc = nom.geocode(address)
    if not loc:
        raise ValueError("failed to get location, None")
    if type(loc) is not Location:
        raise ValueError("failed to get location, Not Location")
    return LocationModel(lat=loc.latitude, lon=loc.longitude)
