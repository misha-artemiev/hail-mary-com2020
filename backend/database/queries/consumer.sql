-- name: GetConsumer :one
SELECT users.user_id, email, fName, lName
FROM consumers
INNER JOIN users ON consumers.user_id=users.user_od
WHERE users.user_id=$1
LIMIT 1;

-- name: CreateConsumer :one
INSERT INTO consumers (user_id, fName, lName)
VALUES ($1, $2, $3);
