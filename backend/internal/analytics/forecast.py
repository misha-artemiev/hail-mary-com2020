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
    
def _no_show_rate(row: ForecastInput) -> float | None:
    """Return the observed no-show rate, or ``None`` when reservations == 0."""
    if row.observed_reservations == 0:
        return None
    return row.observed_no_shows / row.observed_reservations

def _confidence_from_n(n: int) -> float:
    """Map sample count to confidence in [0.05, 0.90] via ``n / (n + 20)``."""
    return min(0.90, n / (n + 20.0))

def _build_rationale(
    n: int,
    avg_reservations: float,
    avg_no_show_rate: float,
    method: str,
    query: ForecastQuery,
    n_categories: int = 1,
) -> str:
    """
    Builds a plain-English explanation of how the forecast was produced.
    
    outputs something like: 
    "Based on 15 past slots (Monday, 09:00-10:00, sunny, 23.5°C), using 
    average of 3 similar slots: avg 12.3 reservations, 20.5% no-show rate."
    
    """
    holiday_note = " (public holiday)" if query.is_holiday else ""
    window = (
        f"{query.window_start_hour.strftime('%H:%M')}"
        f"–{query.window_end_hour.strftime('%H:%M')}"
    )
    slot_word = "slot" if n == 1 else "slots"
    category_note = (
        f", averaged across {n_categories} categories" if n_categories > 1 else ""
    )
    return (
        f"Based on {n} past {slot_word} "
        f"({query.day_of_week.value}{holiday_note}, {window}, "
        f"{query.weather_flag.value}, {float(query.temperature):.1f}°C) "
        f"using {method}{category_note}: "
        f"avg {avg_reservations:.1f} reservations, "
        f"{avg_no_show_rate * 100:.1f}% no-show rate."
    )