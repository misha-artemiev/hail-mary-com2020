-- name: GetConsumer :one
SELECT u.user_id, u.email, c.fName, c.lName, u.last_login, u.created_at
FROM consumers  c
INNER JOIN users u ON c.user_id = u.user_id
WHERE u.user_id=$1
LIMIT 1;

-- name: CreateConsumer :one
INSERT INTO consumers (user_id, fName, lName)
VALUES ($1, $2, $3)
RETURNING *;

-- name: UpdateConsumer :one
UPDATE consumers
SET fName=$2, lName=$3
WHERE user_id=$1
RETURNING *;
