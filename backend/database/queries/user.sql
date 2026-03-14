-- name: GetUser :one
SELECT user_id, username, email, role, created_at
FROM users
WHERE user_id = $1 
LIMIT 1;

-- name: GetUserLogin :one
SELECT user_id, username, email, pw_hash, role
FROM users
WHERE email = $1
LIMIT 1;

-- name: CreateUser :one
INSERT INTO users (email, username, pw_hash, role)
VALUES ($1, $2, $3, $4)
RETURNING user_id, username, email, role, created_at;

-- name: DeleteUser :one
DELETE FROM users
WHERE user_id = $1
RETURNING user_id, username, email, role, created_at;

-- name: UpdateUserEmail :one
UPDATE users
SET email=$2
WHERE user_id=$1
RETURNING user_id, username, email, role, created_at;

-- name: UpdateUserPassword :one
UPDATE users
SET pw_hash=$2
WHERE user_id=$1
RETURNING user_id, username, email, role, created_at;

-- name: GetUsers :many
SELECT user_id, username, email, role, created_at, last_login
FROM users;
