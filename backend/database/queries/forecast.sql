-- name: GetForecastInputsBySeller :many
SELECT input_id, bundle_id, seller_id, category_id, day_of_week, window_start_hour, window_end_hour, is_holiday, temperature, weather_flag, observed_reservations, observed_no_shows
FROM forecast_input
WHERE seller_id = $1;

-- name: CreateForecastInput :one
INSERT INTO forecast_input (bundle_id, seller_id, category_id, day_of_week, window_start_hour, window_end_hour, is_holiday, temperature, weather_flag, observed_reservations, observed_no_shows)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
RETURNING *;

-- name: UpsertForecastOutput :one
INSERT INTO forecast_output (bundle_id, seller_id, window_start, predicted_sales, posted_qty, predicted_no_show_prob, confidence, rationale)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT (bundle_id) DO UPDATE SET
    predicted_sales = EXCLUDED.predicted_sales,
    posted_qty = EXCLUDED.posted_qty,
    predicted_no_show_prob = EXCLUDED.predicted_no_show_prob,
    confidence = EXCLUDED.confidence,
    rationale = EXCLUDED.rationale,
    generated_at = CURRENT_TIMESTAMP
RETURNING *;

-- name: GetForecastOutputsBySeller :many
SELECT output_id, bundle_id, seller_id, window_start, predicted_sales, posted_qty, predicted_no_show_prob, confidence, rationale, generated_at
FROM forecast_output
WHERE seller_id = $1
ORDER BY window_start;

-- name: GetForecastOutputByBundle :one
SELECT output_id, bundle_id, seller_id, window_start, predicted_sales, posted_qty, predicted_no_show_prob, confidence, rationale, generated_at
FROM forecast_output
WHERE bundle_id = $1
LIMIT 1;
