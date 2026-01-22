-- name: GetUser :one
SELECT *
FROM users
WHERE user_id=?
LIMIT 1;

-- name: GetUserByEmail :one
SELECT *
FROM users
WHERE email=?
LIMIT 1;

-- name: CreateUser :exec
INSERT INTO users (email, pw_hash, role)
VALUES (?, ?, ?);
