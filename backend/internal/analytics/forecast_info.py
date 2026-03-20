"""Builds ForecastQuery objects by pulling in weather and holiday data.

Uses Open-Meteo for weather and the holidays library for UK holidays.
Call build_forecast_query() to get a query ready to pass straight into
generate_forecast() in forecast.py.
"""

import datetime
from decimal import Decimal

import holidays
import requests # type: ignore[import-untyped]
from internal.queries.models import DayOfWeek, WeatherFlag
from pydantic import BaseModel

from .forecast import ForecastQuery

# --- Constants ---

_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
_PAST_URL: str = "https://archive-api.open-meteo.com/v1/archive"

_TIMEOUT: int = 10  # seconds

# WMO weather code boundaries used in _wmo_to_flag().
_WMO_SNOWY_MIN: int = 71
_WMO_SNOWY_MAX: int = 86
_WMO_RAINY_MIN: int = 51
_WMO_RAINY_MAX: int = 82
_WMO_WINDY_MIN: int = 95

# date.weekday() returns 0-6 starting Monday — same order DayOfWeek is defined.
_WEEKDAY_TO_ENUM: dict[int, DayOfWeek] = dict(enumerate(DayOfWeek))

# --- Bundle details dataclass ---


class BundleDetails(BaseModel):
    """Groups the basic details of an upcoming bundle for build_forecast_query().

    Keeps the argument count under the linter limit and makes call sites
    easier to read.
    """

    bundle_date: datetime.date
    window_start_hour: datetime.time
    window_end_hour: datetime.time
    seller_id: int
    category_ids: list[int]
    latitude: float
    longitude: float


#  --- Private helpers ---


def _wmo_to_flag(code: int) -> WeatherFlag:
    """Convert a WMO weather code from Open-Meteo into a WeatherFlag.

    WMO ranges:
        0                              -> sunny
        1-48                           -> cloudy
        51-82                          -> rainy
        71-86                          -> snowy
        95+                            -> windy

    Returns:
        A WeatherFlag corresponding to the given WMO code.
    """
    if code == 0:
        return WeatherFlag.SUNNY
    # Snowy must come before rainy. Codes 71-82 sit in both ranges.
    if _WMO_SNOWY_MIN <= code <= _WMO_SNOWY_MAX:
        return WeatherFlag.SNOWY
    if _WMO_RAINY_MIN <= code <= _WMO_RAINY_MAX:
        return WeatherFlag.RAINY
    if code >= _WMO_WINDY_MIN:
        return WeatherFlag.WINDY
    return WeatherFlag.CLOUDY


def _fetch_weather(
    url: str, bundle_date: datetime.date, latitude: float, longitude: float
) -> tuple[Decimal, WeatherFlag]:
    """Pull max temperature and weather for the given date and location.

    Returns:
        A (temperature, WeatherFlag) tuple for the requested date.

    Raises:
        ValueError: Open-Meteo returned no data for the date.
    """
    date_str = bundle_date.isoformat()

    response = requests.get(
        url,
        params={
            "latitude": str(latitude),
            "longitude": str(longitude),
            "daily": "temperature_2m_max,weathercode",
            # Europe/London keeps daily windows aligned with UK midnight.
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
    uk_holidays = holidays.country_holidays("GB")
    return bundle_date in uk_holidays


# --- Public functions ---


def build_forecast_query(bundle: BundleDetails) -> ForecastQuery:
    """Build a ForecastQuery for an upcoming bundle.

    Handles all the external lookups — weather from Open-Meteo and UK bank
    holidays — so the caller just passes in a BundleDetails object.

    Args:
        bundle: The basic details of the upcoming bundle.

    Returns:
        A fully populated ForecastQuery ready for generate_forecast().
    """
    day_of_week = _WEEKDAY_TO_ENUM[bundle.bundle_date.weekday()]
    is_holiday = _is_uk_holiday(bundle.bundle_date)
    temperature, weather_flag = _fetch_weather(
        _FORECAST_URL, bundle.bundle_date, bundle.latitude, bundle.longitude
    )

    return ForecastQuery(
        seller_id=bundle.seller_id,
        category_ids=bundle.category_ids,
        day_of_week=day_of_week,
        window_start_hour=bundle.window_start_hour,
        window_end_hour=bundle.window_end_hour,
        is_holiday=is_holiday,
        temperature=temperature,
        weather_flag=weather_flag,
    )


def fetch_historical_weather(
    bundle_date: datetime.date, latitude: float, longitude: float
) -> tuple[Decimal, WeatherFlag]:
    """Fetch the actual weather conditions for a completed bundle's date.

    Called after a bundle's pickup window closes, before writing the
    forecast_input row. Uses the Open-Meteo archive endpoint which holds
    verified historical records rather than forecast data.

    Args:
        bundle_date: The date the bundle's pickup window fell on.
        latitude: Seller latitude.
        longitude: Seller longitude.

    Returns:
        A (temperature, WeatherFlag) tuple of the actual conditions on that day.
    """
    return _fetch_weather(_PAST_URL, bundle_date, latitude, longitude)
