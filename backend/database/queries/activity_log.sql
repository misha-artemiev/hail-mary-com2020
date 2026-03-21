-- name: CreateActivityLog :one
INSERT INTO activity_log (user_id, action, details, ip_address)
VALUES ($1, $2, $3, $4)
RETURNING *;
