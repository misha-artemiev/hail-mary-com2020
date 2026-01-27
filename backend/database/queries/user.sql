-- name: GetUser :one
SELECT user_id, email, role, created_at
FROM users
WHERE user_id = $1 
LIMIT 1;

-- name: GetUserLogin :one
SELECT user_id, email, pw_hash, role
FROM users
WHERE email = $1
LIMIT 1;

-- name: CreateUser :one
INSERT INTO users (email, pw_hash, role)
VALUES ($1, $2, $3)
RETURNING user_id, email, role, created_at;

-- name: DeleteUser :one
DELETE FROM users
WHERE user_id = $1
RETURNING user_id, email, role, created_at;
