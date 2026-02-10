from geopy.distance import geodesic
from pydantic import BaseModel
from .types import LocationModel


class DistanceBoxModel(BaseModel):
    lat_max: float
    lat_min: float
    lon_max: float
    lon_min: float


def dist_safe_box(loc: LocationModel, dist: int) -> DistanceBoxModel:
    loc_dist = geodesic(dist)

    distance_box = DistanceBoxModel(
        lat_max=loc_dist.destination(loc.lat, 0).latitude,
        lat_min=loc_dist.destination(loc.lat, 180).latitude,
        lon_max=loc_dist.destination(loc.lon, 90).longitude,
        lon_min=loc_dist.destination(loc.lon, 270).longitude,
    )

    return distance_box


def get_distance(from_loc: LocationModel, to_loc: LocationModel) -> float:
    dist = geodesic(
        tuple(from_loc.model_dump().values()), tuple(to_loc.model_dump().values())
    )
    if type(dist) is not geodesic or type(dist) is not float:
        raise ValueError("failed to calculate distance")
    return dist.km
