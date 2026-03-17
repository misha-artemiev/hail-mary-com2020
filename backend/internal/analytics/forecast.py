from __future__ import annotations

import datetime
from decimal import Decimal
from statistics import mean
from typing import Protocol

import numpy as np
from lightgbm import LGBMRegressor
from pydantic import BaseModel

from internal.queries.models import DayOfWeek, ForecastInput, WeatherFlag