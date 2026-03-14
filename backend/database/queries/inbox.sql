-- name: GetInboxes :many
SELECT *
FROM inbox;

-- name: GetUserInbox :many
SELECT *
FROM inbox
WHERE user_id = $1;

-- name: DeleteInboxMessage :one
DELETE FROM inbox
WHERE message_id = $1
RETURNING *;

-- name: CreateInboxMessage :one
INSERT INTO inbox (user_id, sender_id, message_subject, message_text)
VALUES ($1, $2, $3, $4)
RETURNING *;
