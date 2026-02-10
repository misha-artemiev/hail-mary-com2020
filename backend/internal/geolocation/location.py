from geopy.geocoders import Nominatim
from geopy import Location
from .types import LocationModel


async def get_location(address: str) -> LocationModel:
    nom = Nominatim(user_agent="hail mary", timeout=10)
    loc = nom.geocode(address)
    if not loc:
        raise ValueError("failed to get location, None")
    if type(loc) != Location:
        raise ValueError("failed to get location, Not Location")
    return LocationModel(lat=loc.latitude, lon=loc.longitude)
