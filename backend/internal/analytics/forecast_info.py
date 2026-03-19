"""Builds ForecastQuery objects by pulling in weather and holiday data.
 
Uses Open-Meteo for weather and the holidays library
for UK holidays.

Call build_forecast_query() to get a query ready to
pass straight into generate_forecast() in the forecast,py file.
 
"""

import datetime
from decimal import Decimal
 
import holidays
import requests
 
from internal.queries.models import DayOfWeek, WeatherFlag
from .forecast import ForecastQuery
 
_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
_PAST_URL: str = "https://archive-api.open-meteo.com/v1/archive"
_FORECAST_PAST_DAYS: int = 7

_TIMEOUT :int = 10 # seconds

_UK_NATIONS : list[str] = ["ENG", "SCT", "WLS", "NIR"]

# Mapping days of week to integers
_WEEKDAY_TO_ENUM: dict[int, DayOfWeek] = {
    i: day for i, day in enumerate(DayOfWeek)
}