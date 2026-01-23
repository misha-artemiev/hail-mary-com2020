-- name: GetUser :one
SELECT * 
FROM users
WHERE user_id = $1 
LIMIT 1;

-- name: GetUserForLogin :one
SELECT user_id, email, pw_hash 
FROM users
WHERE email = $1
LIMIT 1;
