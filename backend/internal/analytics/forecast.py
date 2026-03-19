"""Forecasting logic for demand prediction of upcoming bundles."""

import datetime
from collections import defaultdict
from decimal import Decimal
from statistics import mean
from typing import Protocol

import numpy as np
from internal.queries.models import DayOfWeek, ForecastInput, WeatherFlag
from lightgbm import LGBMRegressor
from pydantic import BaseModel

# --- Constants ---

# The minimum number of rows required before we trust the ML model.
# Below this threshold we fall back to the similarity-weighted average, which
# is more stable on very small datasets.
_MIN_ML_SAMPLES: int = 10

# Map each enum member to a stable integer index based on definition order.
# LightGBM and numpy can only work with numbers, not enum values, so these
# dictionaries are used inside _encode() to convert before training/predicting.
_DAY_INDEX: dict[DayOfWeek, int] = {}
for i, d in enumerate(DayOfWeek):
    _DAY_INDEX[d] = i

_WEATHER_INDEX: dict[WeatherFlag, int] = {}
for i, w in enumerate(WeatherFlag):
    _WEATHER_INDEX[w] = i

# Cold-start defaults — returned when a seller has zero historical rows for a
# category. Values are intentionally conservative: predict low demand and low
# confidence so the seller is not misled by a guess with no evidence behind it.
_COLD_RESERVATIONS: int = 1
_COLD_NO_SHOW_PROB: Decimal = Decimal("0.1500")
_COLD_CONFIDENCE: Decimal = Decimal("0.0500")
_COLD_RATIONALE: str = (
    "No historical data found for this seller and category. "
    "Forecast is a conservative cold-start estimate."
)

# --- Models ---


class ForecastQuery(BaseModel):
    """The conditions of an upcoming bundle to forecast demand for."""

    seller_id: int
    # A bundle can belong to more than one category. We forecast each category
    # separately and average the results, so this is a list rather than a
    # single int. See generate_forecast() for how the averaging works.
    category_ids: list[int]
    day_of_week: DayOfWeek
    window_start_hour: datetime.time
    window_end_hour: datetime.time
    is_holiday: bool
    temperature: Decimal
    weather_flag: WeatherFlag


class ForecastResult(BaseModel):
    """Forecast prediction ready to be written to "forecast_output"."""

    bundle_id: int
    predicted_reservations: int
    predicted_no_show_prob: Decimal
    confidence: Decimal
    # Nullable, cold-start results use the shared _COLD_RATIONALE constant,
    # but we allow None.
    rationale: str | None


# --- Helpers ---


class _HasFeatures(Protocol):
    """Structural protocol shared by ForecastInput and ForecastQuery.

    Both types carry the same six condition fields. Declaring this protocol
    lets _encode() accept either type without them needing a shared base class.
    """

    day_of_week: DayOfWeek
    window_start_hour: datetime.time
    window_end_hour: datetime.time
    is_holiday: bool
    temperature: Decimal
    weather_flag: WeatherFlag


def _encode(obj: _HasFeatures) -> list[float]:
    """Encode any object matching _HasFeatures into a  feature vector.

    Feature order: [day_of_week, window_start, window_end,
                    is_holiday, temperature, weather_flag]

    The order here should stay the same LightGBM trains on columns by position,
    so the query vector must be built in exactly the same order as the
    training matrix.

    Returns:
        A list of floats representing the encoded features.
    """
    return [
        float(_DAY_INDEX[obj.day_of_week]),
        # Convert time to a decimal hour so 9:30 becomes 9.5, 14:15 becomes
        # 14.25, etc.
        obj.window_start_hour.hour + obj.window_start_hour.minute / 60.0,
        obj.window_end_hour.hour + obj.window_end_hour.minute / 60.0,
        # bool must be cast to float LightGBM expects all
        # features to be the same numeric type.
        float(obj.is_holiday),
        float(obj.temperature),
        float(_WEATHER_INDEX[obj.weather_flag]),
    ]


def _no_show_rate(row: ForecastInput) -> float | None:
    """Return the observed no-show rate, or None when reservations == 0.

    We return None rather than 0.0 when there were no reservations because
    0.0 would imply a perfect attendance rate, which is misleading.
    """
    if row.observed_reservations == 0:
        return None
    return row.observed_no_shows / row.observed_reservations


def _confidence_from_n(n: int) -> float:
    """Map sample count to a confidence score in range [0.05, 0.90].

    Uses the formula n / (n + 20) which grows quickly at first then levels
    off, 10 rows gives 0.33, 20 rows gives 0.50, 80 rows gives 0.80.
    Capped at 0.90 so confidence never reaches 1.0.

    Returns:
        A confidence score between 0.05 and 0.90.
    """
    return min(0.90, n / (n + 20.0))


def _build_rationale(
    n: int,
    avg_reservations: float,
    avg_no_show_rate: float,
    method: str,
    query: ForecastQuery,
) -> str:
    """Build a plain-English explanation of how the forecast was produced.

    Outputs something like:
    "Based on 15 past slots (Monday, 09:00-12:00, rainy, 8.5 degrees C)
    using LightGBM: avg 6.3 reservations, 18.0% no-show rate."

    Returns:
        A string explanation of the forecast.
    """
    # Only append the holiday note when relevant
    # for the common case where it is not a public holiday.
    holiday_note = " (public holiday)" if query.is_holiday else ""

    window = (
        f"{query.window_start_hour.strftime('%H:%M')}"
        f"-{query.window_end_hour.strftime('%H:%M')}"
    )

    # Grammatically correct singular/plural so the output reads naturally.
    slot_word = "slot" if n == 1 else "slots"

    return (
        f"Based on {n} past {slot_word} "
        f"({query.day_of_week.value}{holiday_note}, {window}, "
        f"{query.weather_flag.value}, {float(query.temperature):.1f}°C) "
        f"using {method}: "
        f"avg {avg_reservations:.1f} reservations, "
        # Multiply by 100 to display as a percentage rather than a decimal.
        f"{avg_no_show_rate * 100:.1f}% no-show rate."
    )


# --- Private prediction functions ---


def _forecast_single_category(
    subset: list[ForecastInput], query: ForecastQuery, bundle_id: int
) -> ForecastResult:
    """Run a forecast for a single category and return the raw result.

    Expects "subset" to already be filtered to the relevant seller and
    category. This function
    can be reused by generate_seller_forecasts(), which pre-groups
    history once and passes the correct slice directly.

    Returns:
        A ForecastResult with predictions for the category.
    """
    n = len(subset)

    # if no history exists for this category, return the
    # cold-start defaults.
    if n == 0:
        return ForecastResult(
            bundle_id=bundle_id,
            predicted_reservations=_COLD_RESERVATIONS,
            predicted_no_show_prob=_COLD_NO_SHOW_PROB,
            confidence=_COLD_CONFIDENCE,
            rationale=_COLD_RATIONALE,
        )

    # Choose the prediction method based on how much data we have.
    # LightGBM needs enough rows to build meaningful decision trees;
    # the weighted average is more stable on very small samples.
    if n >= _MIN_ML_SAMPLES:
        pred_res, pred_ns = _predict_with_lgbm(subset, query)
        method = "LightGBM"
    else:
        pred_res, pred_ns = _predict_weighted_avg(subset, query)
        method = "similarity-weighted average"

    # Round reservations to a whole number, you can't have half a reservation.
    # max(0, ...) prevents a negative prediction reaching the database if the
    # model produces one.
    predicted_reservations = max(0, round(pred_res))

    # Clip the no-show probability to a valid range.
    predicted_no_show_prob = float(np.clip(pred_ns, 0.0, 1.0))

    # These averages are used only in the rationale string to give the seller
    # context on what the prediction is based on.
    avg_res = mean(r.observed_reservations for r in subset)
    no_show_rates = [rate for r in subset if (rate := _no_show_rate(r)) is not None]
    # Default to 0.0 if every historical row had zero reservations and produced
    # no valid rate, mean() would raise a StatisticsError on an empty list.
    avg_no_show = mean(no_show_rates) if no_show_rates else 0.0

    return ForecastResult(
        bundle_id=bundle_id,
        predicted_reservations=predicted_reservations,
        # Convert via string to avoid floating point not being precise
        # round() pins it to 4 decimal places to
        # match the DECIMAL(5,4) column in forecast_output.
        predicted_no_show_prob=Decimal(str(round(predicted_no_show_prob, 4))),
        confidence=Decimal(str(round(_confidence_from_n(n), 4))),
        rationale=_build_rationale(n, avg_res, avg_no_show, method, query),
    )


def _average_category_results(
    results: list[ForecastResult], bundle_id: int
) -> ForecastResult:
    """Average a list of per-category ForecastResults into one final result.

    Used by both generate_forecast() and generate_seller_forecasts() so the
    averaging logic lives in one place. If the
    averaging behaviour ever changes, there is one place to update.

    Returns:
        A single ForecastResult with averaged predictions.
    """
    avg_reservations = mean(r.predicted_reservations for r in results)
    # float() is needed here because predicted_no_show_prob and confidence are
    # stored as Decimal on each result, converting to float first keeps things
    # consistent before we round and convert back to Decimal at the end.
    avg_no_show_prob = mean(float(r.predicted_no_show_prob) for r in results)
    avg_confidence = mean(float(r.confidence) for r in results)

    n_categories = len(results)

    if n_categories == 1:
        # Single category, pass through the full detailed rationale that
        # _forecast_single_category already built. Output is identical to
        # what the original single-category design produced.
        rationale = results[0].rationale
    else:
        # Multiple categories, replace the per-category rationale with a
        # short summary.
        rationale = (
            f"Multi-category forecast (averaged across {n_categories} categories)."
        )

    return ForecastResult(
        bundle_id=bundle_id,
        # Round to the nearest integer, fractional reservations are meaningless.
        # max(0, ...) prevents a negative average.
        predicted_reservations=max(0, round(avg_reservations)),
        predicted_no_show_prob=Decimal(str(round(avg_no_show_prob, 4))),
        confidence=Decimal(str(round(avg_confidence, 4))),
        rationale=rationale,
    )


# --- Public ---


def generate_forecast(
    history: list[ForecastInput], query: ForecastQuery, bundle_id: int
) -> ForecastResult:
    """Generate a reservation and no-show forecast for an upcoming bundle.

    Runs a separate forecast for each category in query.category_ids,
    then averages the results via _average_category_results.

    Args:
        history: All forecast_input rows for this seller.
        query: The conditions of the upcoming bundle.
        bundle_id: The bundle this forecast is attached to.

    Returns:
        A ForecastResult ready to insert into forecast_output.
    """
    # Run one forecast per category. Each call receives only the rows that
    # match both the seller and that specific category. For forecasting many
    # bundles at once, use generate_seller_forecasts() instead, which
    # pre-groups the history once upfront and avoids scanning the full list
    # on every category call.
    results = [
        _forecast_single_category(
            [
                r
                for r in history
                if r.seller_id == query.seller_id and r.category_id == category_id
            ],
            query,
            bundle_id,
        )
        for category_id in query.category_ids
    ]
    return _average_category_results(results, bundle_id)


def generate_seller_forecasts(
    history: list[ForecastInput], bundles: list[tuple[int, ForecastQuery]]
) -> list[ForecastResult]:
    """Generate forecasts for all of a seller's upcoming bundles.

    Pre-groups history by category once upfront.

    Args:
        history: All forecast_input rows for this seller.
        bundles: A list of (bundle_id, ForecastQuery) pairs — one per
            upcoming bundle to forecast.

    Returns:
        A list of ForecastResult objects ready to insert into
        forecast_output, in the same order as bundles.
    """
    # Build a dictionary keyed by category_id so each lookup is instant.
    # defaultdict(list) means we never need to check whether a key exists
    # before appending it creates an empty list automatically on first access.
    history_by_category: dict[int, list[ForecastInput]] = defaultdict(list)
    for row in history:
        history_by_category[row.category_id].append(row)

    results = []
    for bundle_id, query in bundles:
        # For each bundle, gather one forecast per category using the
        # pre-grouped dictionary. history_by_category[category_id] returns
        # an empty list if that category has no history,
        # which then uses the cold-start path inside _forecast_single_category.
        per_category = [
            _forecast_single_category(
                history_by_category[category_id], query, bundle_id
            )
            for category_id in query.category_ids
        ]
        results.append(_average_category_results(per_category, bundle_id))

    # The order of results matches the order of bundles.
    return results


# --- Private prediction functions ---


def _predict_with_lgbm(
    subset: list[ForecastInput], query: ForecastQuery
) -> tuple[float, float]:
    """Train LightGBM regressors on subset and predict for query.

    Trains two completely separate models, one for reservation count and one
    for no-show rate.

    n_estimators scales with sample count (50-200) to avoid overfitting
    small datasets while still giving full power on larger ones.
    verbose=-1 removes training logs on every call.

    Returns:
        (predicted_reservations, predicted_no_show_rate)
    """
    # Build the feature matrix, each row is one historical bundle encoded
    # as a vector of 6 numbers. (n_samples, 6).
    x_all = np.array([_encode(r) for r in subset], dtype=float)

    # Building the target vector for the reservations model.
    # Shape: (n_samples,), one count per row.
    y_res = np.array([r.observed_reservations for r in subset], dtype=float)

    # Encode the upcoming bundle's conditions in the same format as the
    # training rows. The extra [] wrapping produces shape (1, 6) rather than
    # (6,) predict() needs 2D input.
    q_vec = np.array([_encode(query)], dtype=float)

    # Scale tree count to dataset size. More trees improve accuracy on larger
    # datasets but risk overfitting when samples are scarce.
    # never goes below 50 tress and above 200
    n_estimators = len(subset)
    n_estimators = max(n_estimators, 50)
    n_estimators = min(n_estimators, 200)

    # Train the reservations model and predict.
    lgbm_res = LGBMRegressor(n_estimators=n_estimators, random_state=42, verbose=-1)
    lgbm_res.fit(x_all, y_res)
    # np.asarray().flat[0] safely extracts the scalar
    pred_res = float(np.asarray(lgbm_res.predict(q_vec)).flat[0])

    # Calculate no-show rates for each historical row. Rows with zero
    # reservations return None and must be excluded from training.
    ns_rates = [_no_show_rate(r) for r in subset]

    # Boolean masking is True for rows that have a valid no-show rate.
    # Used to filter both the feature matrix and the target vector together
    # so their lengths stay aligned.
    valid_mask = np.array([v is not None for v in ns_rates])

    if valid_mask.any():
        y_ns = np.array([v for v in ns_rates if v is not None], dtype=float)
        lgbm_ns = LGBMRegressor(n_estimators=n_estimators, random_state=42, verbose=-1)
        # x_all[valid_mask] uses numpy boolean indexing to select only the
        # rows that have a valid no-show rate
        lgbm_ns.fit(x_all[valid_mask], y_ns)
        pred_ns = float(np.asarray(lgbm_ns.predict(q_vec)).flat[0])
    else:
        # if every historical row has zero reservations so no no-show model can
        # be trained. Default to 0.0 to avoid crash.
        pred_ns = 0.0

    return pred_res, pred_ns


def _predict_weighted_avg(
    subset: list[ForecastInput], query: ForecastQuery
) -> tuple[float, float]:
    """Predict using a similarity-weighted average.

    Each historical row earns a similarity score based on how closely its
    conditions match the upcoming bundle. Scores are then normalised into
    weights that sum to 1.0 and used to compute a weighted average of the
    observed reservation counts and no-show rates.

    Row weights:

    - day_of_week exact match       → +2.0
    - window_start proximity (±2 h) → up to +1.5
    - is_holiday exact match        → +1.5
    - weather_flag exact match      → +1.0
    - temperature proximity (±5°C) → up to +0.5

    Returns:
        (predicted_reservations, predicted_no_show_rate)
    """
    # Pre-compute the query's start time and temperature as plain floats once
    # so we don't repeat the same conversion inside the loop on every row.
    q_start = query.window_start_hour.hour + query.window_start_hour.minute / 60.0
    q_temp = float(query.temperature)

    weights: list[float] = []
    res_vals: list[float] = []
    ns_vals: list[float] = []

    for row in subset:
        score = 0.0

        # Day of week is the strongest predictor — a Monday bundle's history
        # is far more relevant to a future Monday than a Saturday's history.
        if row.day_of_week == query.day_of_week:
            score += 2.0

        # Proximity score for time of day higher weight for closeness rather than
        # requiring an exact match. Drops to 0 at 2 hours difference.
        hour_diff = abs(
            (row.window_start_hour.hour + row.window_start_hour.minute / 60.0) - q_start
        )
        score += max(0.0, 1.5 * (1.0 - hour_diff / 2.0))

        # Holiday status is nearly as important as day of week — demand on a
        # bank holiday behaves very differently to a normal weekday.
        if row.is_holiday == query.is_holiday:
            score += 1.5

        # Exact weather match. Weighted lower than day and holiday because
        # weather affects demand but is less dominant than day-level patterns.
        if row.weather_flag == query.weather_flag:
            score += 1.0

        # Proximity score for temperature — full points for identical temp,
        # dropping to 0 at 5°C difference. Lowest weighted feature because
        # the weather flag already captures most of the temperature signal.
        score += max(0.0, 0.5 * (1.0 - abs(float(row.temperature) - q_temp) / 5.0))

        # flooring weight just above zero.
        # avoids division by 0 error.
        weights.append(max(score, 1e-6))
        res_vals.append(float(row.observed_reservations))

        # Substitute 0.0 for rows with no calculable no-show rate (zero
        # reservations). Unlike the LightGBM path which skips these rows,
        # the weighted average needs all three lists to stay the same length
        # so the dot product aligns correctly.
        rate = _no_show_rate(row)
        ns_vals.append(rate if rate is not None else 0.0)

    # Normalise the raw scores so they sum to 1.0, converting them from
    # arbitrary similarity points into proper proportional weights.
    w_norm = np.array(weights, dtype=float)
    w_norm /= w_norm.sum()

    # Dot product: multiply each weight by its corresponding value and sum.
    # A row with weight 0.4 and 8 reservations contributes 3.2 to the total.
    return float(np.dot(w_norm, res_vals)), float(np.dot(w_norm, ns_vals))


