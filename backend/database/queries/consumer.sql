-- name: GetConsumer :one
SELECT users.user_id, email, fName, lName
FROM consumers
INNER JOIN users ON consumers.user_id=users.user_od
WHERE users.user_id=?
LIMIT 1;

-- name: CreateConsumer :execresult
INSERT INTO consumers (user_id, fName, lName)
VALUES (?, ?, ?);
