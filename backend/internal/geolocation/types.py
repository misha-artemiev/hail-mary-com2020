from pydantic import BaseModel


class LocationModel(BaseModel):
    lat: float
    lon: float
