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

