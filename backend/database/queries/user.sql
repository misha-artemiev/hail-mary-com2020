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

-- name: LeaderboardReservations :many
SELECT u.username, COUNT(r.reservation_id) AS reservation_count
FROM users u
LEFT JOIN reservations r ON r.consumer_id = u.user_id
GROUP BY u.user_id, u.username
ORDER BY reservation_count DESC
LIMIT $1;

-- name: LeaderboardCarbonDioxide :many
SELECT u.username, COALESCE(SUM(b.carbon_dioxide), 0)::numeric AS total_carbon_dioxide
FROM users u
LEFT JOIN reservations r ON r.consumer_id = u.user_id
LEFT JOIN bundles b ON b.bundle_id = r.bundle_id
GROUP BY u.user_id, u.username
ORDER BY total_carbon_dioxide DESC
LIMIT $1;
