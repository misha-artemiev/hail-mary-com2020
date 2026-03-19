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

# --- Helper functions ---

def _wmo_to_flag(code: int) -> WeatherFlag:
    """Convert a WMO weather code from Open-Meteo into a WeatherFlag.
 
    WMO ranges:
        0         → sunny
        1-48      → cloudy
        51-82     → rainy
        71-86     → snowy
        95+       → windy
        
    Returns: a WeatherFlag corresponding to the given WMO code.
    """
    if code == 0:
        return WeatherFlag.sunny
    # Snowy must come before rainy, codes 71-82 sit in both ranges.
    if 71 <= code <= 86:
        return WeatherFlag.snowy
    if 51 <= code <= 82:
        return WeatherFlag.rainy
    if code >= 95:
        return WeatherFlag.windy
    return WeatherFlag.cloudy
 
 
def _fetch_weather(
    bundle_date: datetime.date,
    latitude: float,
    longitude: float,
) -> tuple[Decimal, WeatherFlag]:
    """Pull max temperature and weather forecast for the given date and location."""
    date_str = bundle_date.isoformat()
 
    response = requests.get(
        _FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,weathercode",
            # Europe/London keeps daily windows aligned with UK midnight,
            # not UTC (they differ by an hour during BST).
            "timezone": "Europe/London",
            "start_date": date_str,
            "end_date": date_str,
        },
        timeout=_TIMEOUT,
    )
    response.raise_for_status()
 
    daily = response.json()["daily"]
    # API always returns lists even for a single date.
    temperatures: list[float] = daily["temperature_2m_max"]
    weather_codes: list[int] = daily["weathercode"]
 
    if not temperatures or temperatures[0] is None:
        raise ValueError(
            f"Open-Meteo returned no data for {date_str} at ({latitude}, {longitude})."
        )
 
    temperature = Decimal(str(round(temperatures[0], 2)))
    weather_flag = _wmo_to_flag(int(weather_codes[0]))
 
    return temperature, weather_flag
 
 
def _is_uk_holiday(bundle_date: datetime.date) -> bool:
    """Return True if the date is a bank holiday anywhere in the UK."""
    for nation in _UK_NATIONS:
        if bundle_date in holidays.country_holidays("GB", nation=nation):
            return True
    return False

# --- Main function ---

def build_forecast_query(
    bundle_date: datetime.date,
    window_start_hour: datetime.time,
    window_end_hour: datetime.time,
    seller_id: int,
    category_ids: list[int],
    latitude: float,
    longitude: float,
) -> ForecastQuery:
    """Build a ForecastQuery for an upcoming bundle.
 
    Handles all the external lookups — weather from Open-Meteo and UK bank
    holidays — so the caller just passes in the bundle's basic details.
 
    Args:
        bundle_date: The date the pickup window falls on.
        window_start_hour: When the pickup window opens, e.g. time(9, 0).
        window_end_hour: When the pickup window closes, e.g. time(12, 0).
        seller_id: The seller posting the bundle.
        category_ids: One or more category IDs the bundle is tagged with.
        latitude: Seller latitude — used to get location-accurate weather.
        longitude: Seller longitude — used to get location-accurate weather.
 
    Returns:
        A fully populated ForecastQuery ready for generate_forecast().
 
    Raises:
        requests.HTTPError: Open-Meteo returned a non-2xx response.
        ValueError: Open-Meteo returned no weather data for the date.
    """
    day_of_week = _WEEKDAY_TO_ENUM[bundle_date.weekday()]
    is_holiday = _is_uk_holiday(bundle_date)
    temperature, weather_flag = _fetch_weather(
        _FORECAST_URL, bundle_date, latitude, longitude
    )
 
    return ForecastQuery(
        seller_id=seller_id,
        category_ids=category_ids,
        day_of_week=day_of_week,
        window_start_hour=window_start_hour,
        window_end_hour=window_end_hour,
        is_holiday=is_holiday,
        temperature=temperature,
        weather_flag=weather_flag,
    )
 
 
def fetch_historical_weather(
    bundle_date: datetime.date,
    latitude: float,
    longitude: float,
) -> tuple[Decimal, WeatherFlag]:
    """Fetch the actual weather conditions for a completed bundle's date.
 
    Called after a bundle's pickup window closes, before writing the
    forecast_input row. Uses the Open-Meteo archive endpoint which holds
    verified historical records rather than forecast data.
 
    Returns a (temperature, WeatherFlag) tuple ready to slot directly
    into the forecast_input row alongside the observed reservation counts.
 
    Args:
        bundle_date: The date the bundle's pickup window fell on.
        latitude: Seller latitude.
        longitude: Seller longitude.
 
    Returns:
        (temperature, weather_flag) — the actual conditions on that day.
 
    Raises:
        requests.HTTPError: Open-Meteo returned a non-2xx response.
        ValueError: Open-Meteo returned no data for the date.
    """
    return _fetch_weather(_PAST_URL, bundle_date, latitude, longitude)