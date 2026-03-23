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

-- name: GetUserId :one
SELECT user_id, role
FROM users
WHERE username=$1
LIMIT 1;

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

-- name: LeaderboardMoneySaved :many
SELECT u.username, COALESCE(SUM(b.price * b.discount_percentage / (100.0 - b.discount_percentage)), 0)::numeric AS total_money_saved
FROM users u
LEFT JOIN reservations r ON r.consumer_id = u.user_id
LEFT JOIN bundles b ON b.bundle_id = r.bundle_id
GROUP BY u.user_id, u.username
ORDER BY total_money_saved DESC
LIMIT $1;

-- name: LeaderboardTotalSpent :many
SELECT u.username, COALESCE(SUM(b.price), 0)::numeric AS total_spent
FROM users u
LEFT JOIN reservations r ON r.consumer_id = u.user_id
LEFT JOIN bundles b ON b.bundle_id = r.bundle_id
GROUP BY u.user_id, u.username
ORDER BY total_spent DESC
LIMIT $1;

-- name: LeaderboardWeeklyStreak :many
WITH weekly_counts AS (
    SELECT u.user_id, u.username,
           DATE_TRUNC('week', r.reserved_at) AS week_start
    FROM users u
    LEFT JOIN reservations r ON r.consumer_id = u.user_id
    WHERE r.reserved_at IS NOT NULL
    GROUP BY u.user_id, u.username, week_start
),
streaks AS (
    SELECT username,
           week_start,
           week_start - INTERVAL '1 week' * ROW_NUMBER() OVER (PARTITION BY username ORDER BY week_start) AS grp
    FROM weekly_counts
)
SELECT username, COUNT(*)::int AS streak_weeks
FROM streaks
GROUP BY username
ORDER BY streak_weeks DESC
LIMIT $1;
