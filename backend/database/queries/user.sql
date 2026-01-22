-- name: GetUser :one
SELECT *
FROM users
WHERE user_id=?
LIMIT 1;

-- name: CreateUser :execresult
INSERT INTO users (email, pw_hash, role)
VALUES (?, ?, ?);
