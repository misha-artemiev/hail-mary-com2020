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
 