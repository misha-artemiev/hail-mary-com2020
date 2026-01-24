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
