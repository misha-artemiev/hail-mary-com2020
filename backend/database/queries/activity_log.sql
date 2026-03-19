-- name: CreateActivityLog :one
INSERT INTO activity_log (user_id, user_role, action, resource_type, resource_id, details, ip_address)
VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING *;
