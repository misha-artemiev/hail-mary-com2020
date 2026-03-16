"""Types for geolocation module."""

from pydantic import BaseModel


class LocationModel(BaseModel):
    """Set of coordinates."""

    lat: float | None
    lon: float | None
