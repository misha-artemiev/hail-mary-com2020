-- name: GetSessionByToken :one
SELECT u.user_id, u.username, u.email, u.role, t.token, t.expires_at, t.created_at
FROM token t
JOIN users u ON u.user_id = t.user_id
WHERE t.token = $1
AND t.expires_at > NOW()
LIMIT 1;

-- name: CreateToken :one
INSERT INTO token (user_id, token, expires_at)
VALUES ($1, $2, $3)
RETURNING *;

-- name: DeleteToken :one
DELETE FROM token
WHERE token = $1
RETURNING *;
