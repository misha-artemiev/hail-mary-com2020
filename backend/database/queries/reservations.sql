-- name: CreateReservation :one
INSERT INTO reservations (bundle_id, consumer_id, claim_code)
VALUES ($1,$2,$3)
RETURNING *;

-- name: GetConsumersReservations :many
SELECT *
FROM reservations
WHERE consumer_id=$1;

-- name: GetBundleReservations :many
SELECT *
FROM reservations
WHERE bundle_id=$1;

-- name: GetReservation :one
SELECT *
FROM reservations
WHERE reservation_id=$1;

-- name: CollectReservation :one
UPDATE reservations
SET collected_at=NOW()
WHERE reservation_id=$1
RETURNING *;

-- name: GetReservationCollection :one
SELECT *
FROM reservations
WHERE bundle_id=$1 AND claim_code=$2 AND collected_at IS NULL
LIMIT 1;

-- name: GetConsumersReservationsFull :many
SELECT r.reservation_id, r.bundle_id, r.reserved_at, r.collected_at, b.seller_id, b.carbon_dioxide, b.window_start, b.window_end, bc.category_id
FROM reservations r
INNER JOIN bundles b ON b.bundle_id = r.bundle_id
LEFT JOIN bundle_category bc ON bc.bundle_id = r.bundle_id
WHERE consumer_id=$1;

-- name: GetReservations :many
SELECT * FROM reservations;

-- name: DeleteReservation :one
DELETE FROM reservations
WHERE reservation_id = $1
RETURNING *;
