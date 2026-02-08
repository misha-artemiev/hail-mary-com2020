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

-- name: UpdateReservationStatus :one
UPDATE reservations
SET status=$2
WHERE reservation_id=$1
RETURNING *;
