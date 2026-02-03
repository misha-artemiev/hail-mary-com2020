-- name: CreateBundle :one
INSERT INTO bundles (seller_id, bundle_name, description, total_qty, price, discount_percentage, window_start, window_end)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING *;

-- name: GetBundle :one
SELECT *
FROM bundles
WHERE bundle_id=$1
LIMIT 1;
