-- name: CreateBundle :one
INSERT INTO bundles (seller_id, bundle_name, description, total_qty, price, discount_percentage, window_start, window_end)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING *;

-- name: GetBundle :one
SELECT *
FROM bundles
WHERE bundle_id=$1
LIMIT 1;

-- name: GetBundles :many
SELECT *
FROM bundles;

-- name: UpdateBundle :one
UPDATE bundles
SET bundle_name=$3, description=$4, total_qty=$5, price=$6, discount_percentage=$7, window_start=$8, window_end=$9
WHERE bundle_id=$1 AND seller_id=$2
RETURNING *;
