-- name: CreateAdmin :one
INSERT INTO admins (user_id, fName, lName)
VALUES ($1,$2,$3)
RETURNING *;

-- name: SetIsAdminActive :one
UPDATE admins
SET active=$2
WHERE user_id=$1
RETURNING *;
