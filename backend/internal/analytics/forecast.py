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