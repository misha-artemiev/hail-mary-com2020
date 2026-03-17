"""Forecasting logic for demand prediction of upcoming bundles."""

from __future__ import annotations

import datetime
from decimal import Decimal
from statistics import mean
from typing import Protocol

import numpy as np
from lightgbm import LGBMRegressor
from pydantic import BaseModel

from internal.queries.models import DayOfWeek, ForecastInput, WeatherFlag

_MIN_ML_SAMPLES: int = 10

_DAY_INDEX: dict[DayOfWeek, int] = {m: i for i, m in enumerate(DayOfWeek)}
_WEATHER_INDEX: dict[WeatherFlag, int] = {m: i for i, m in enumerate(WeatherFlag)}

_COLD_RESERVATIONS: int = 1
_COLD_NO_SHOW_PROB: Decimal = Decimal("0.1500")
_COLD_CONFIDENCE: Decimal = Decimal("0.0500")
_COLD_RATIONALE: str = (
    "No historical data found for this seller and category. "
    "Forecast is a conservative cold-start estimate."
)

class ForecastQuery(BaseModel):
    """The conditions of an upcoming bundle to forecast demand for."""

    seller_id: int
    category_id: list[int]
    day_of_week: DayOfWeek
    window_start_hour: datetime.time
    window_end_hour: datetime.time
    is_holiday: bool
    temperature: Decimal
    weather_flag: WeatherFlag


class ForecastResult(BaseModel):
    """Forecast prediction ready to be written to ``forecast_output``."""

    bundle_id: int
    predicted_reservations: int
    predicted_no_show_prob: Decimal
    confidence: Decimal
    rationale: str | None
    
class _HasFeatures(Protocol):
    """Structural protocol shared by ForecastInput and ForecastQuery."""

    day_of_week: DayOfWeek
    window_start_hour: datetime.time
    window_end_hour: datetime.time
    is_holiday: bool
    temperature: Decimal
    weather_flag: WeatherFlag
    
def _encode(obj: _HasFeatures) -> list[float]:
    """
    Encode any object matching ``_HasFeatures`` into a numeric vector of features
    for the forecasting model.
        
    Feature order: [day_of_week, window_start, window_end,
                    is_holiday, temperature, weather_flag]
    """
    return [
        float(_DAY_INDEX[obj.day_of_week]),
        obj.window_start_hour.hour + obj.window_start_hour.minute / 60.0, #e.g 9:30 -> 9.5
        obj.window_end_hour.hour + obj.window_end_hour.minute / 60.0,
        float(obj.is_holiday),
        float(obj.temperature),
        float(_WEATHER_INDEX[obj.weather_flag]),
    ]