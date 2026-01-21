-- name: GetUser :one
SELECT * 
FROM users
WHERE user_id = ? 
LIMIT 1;

-- name: GetUserForLogin :one
SELECT user_id, email, password_hash 
FROM users
WHERE email = ?
LIMIT 1;
