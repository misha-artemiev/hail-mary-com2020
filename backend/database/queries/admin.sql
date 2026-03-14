-- name: CreateAdmin :one
INSERT INTO admins (user_id, fName, lName)
VALUES ($1,$2,$3)
RETURNING *;

-- name: SetIsAdminActive :one
UPDATE admins
SET active=$2
WHERE user_id=$1
RETURNING *;

-- name: GetAdmin :one
SELECT u.user_id, u.username, u.email, a.fName, a.lName, a.active, u.last_login, u.created_at
FROM admins a
INNER JOIN users u ON a.user_id = u.user_id
WHERE u.user_id = $1
LIMIT 1;

-- name: GetAdmins :many
SELECT u.user_id, u.username, u.email, a.fName, a.lName, a.active, u.last_login, u.created_at
FROM admins a
INNER JOIN users u ON a.user_id = u.user_id;

-- name: UpdateAdmin :one
UPDATE admins
SET fName = $2, lName = $3
WHERE user_id = $1
RETURNING *;
