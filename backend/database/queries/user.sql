-- name: GetUser :one
SELECT *
FROM users
<<<<<<< HEAD
WHERE user_id=?
LIMIT 1;

-- name: GetUserByEmail :one
SELECT *
FROM users
WHERE email=?
=======
WHERE user_id = $1 
LIMIT 1;

-- name: GetUserForLogin :one
SELECT user_id, email, pw_hash 
FROM users
WHERE email = $1
>>>>>>> origin/release
LIMIT 1;

-- name: CreateUser :exec
INSERT INTO users (email, pw_hash, role)
VALUES (?, ?, ?);
