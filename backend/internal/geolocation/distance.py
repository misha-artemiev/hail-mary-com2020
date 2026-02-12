"""Distance calculation modules."""

from geopy.distance import geodesic  # type: ignore[import-untyped]
from pydantic import BaseModel

from .types import LocationModel


class DistanceBoxModel(BaseModel):
    """Safe distance box for database query."""

    lat_max: float
    lat_min: float
    lon_max: float
    lon_min: float


def dist_safe_box(loc: LocationModel, dist: int) -> DistanceBoxModel:
    """Calculate safe box for database query.

    Args:
      loc: start point coordinates
      dist: distance from the point

    Returns:
        safe box borders
    """
    loc_dist = geodesic(dist)
    loc_point = tuple(loc.model_dump().values())
    return DistanceBoxModel(
        lat_max=loc_dist.destination(loc_point, 0).latitude,
        lat_min=loc_dist.destination(loc_point, 180).latitude,
        lon_max=loc_dist.destination(loc_point, 90).longitude,
        lon_min=loc_dist.destination(loc_point, 270).longitude,
    )


def get_distance(from_loc: LocationModel, to_loc: LocationModel) -> float:
    """Geographical distance between two points.

    Args:
      from_loc: from point
      to_loc: to point

    Returns:
      distance between points in kilometers

    Raises:
      ValueError: if failed to get distance
    """
    dist = geodesic(
        tuple(from_loc.model_dump().values()), tuple(to_loc.model_dump().values())
    )
    if type(dist) is not geodesic:
        raise ValueError("failed to calculate distance")
    return float(dist.km)
