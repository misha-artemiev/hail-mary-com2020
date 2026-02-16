"""Location translation."""

from hashlib import blake2b

from geopy import Location  # type: ignore[import-untyped]
from geopy.exc import GeocoderServiceError  # type: ignore[import-untyped]
from geopy.geocoders import Nominatim  # type: ignore[import-untyped]

from .types import LocationModel

FALLBACK_EXETER_CENTRE = LocationModel(lat=50.7260, lon=-3.5275)
"""Fallback point used when geocoding is unavailable."""


def _fallback_location(address: str) -> LocationModel:
    """Create a deterministic fallback coordinate near Exeter."""
    digest = blake2b(address.encode("utf-8"), digest_size=2).digest()
    lat_offset = ((digest[0] / 255.0) - 0.5) * 0.04
    lon_offset = ((digest[1] / 255.0) - 0.5) * 0.06
    return LocationModel(
        lat=FALLBACK_EXETER_CENTRE.lat + lat_offset,
        lon=FALLBACK_EXETER_CENTRE.lon + lon_offset,
    )


def get_location(address: str) -> LocationModel:
    """Coordinates from Address.

    Args:
      address: real address

    Returns:
      coordinates of the address

    Falls back to a deterministic Exeter coordinate if geocoding is unavailable
    (for example SSL/certificate/network failures in local development).
    """
    nom = Nominatim(user_agent="hail mary", timeout=10)
    try:
        loc = nom.geocode(address)
    except GeocoderServiceError:
        return _fallback_location(address)

    if not loc:
        return _fallback_location(address)
    if type(loc) is not Location:
        return _fallback_location(address)
    return LocationModel(lat=loc.latitude, lon=loc.longitude)
