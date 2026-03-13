-- name: GetBadge :one
SELECT *
FROM badges
WHERE badge_id = $1
LIMIT 1;

-- name: GetConsumerBadges :many
SELECT b.badge_id, b.name, b.description, ba.level, ba.acquired_at
FROM badges b
INNER JOIN badges_acquired ba ON ba.badge_id = b.badge_id
WHERE ba.user_id = $1;

-- name: GetBadges :many
SELECT *
FROM badges;

-- name: AcquireBadge :one
INSERT INTO badges_acquired (user_id, badge_id, level)
VALUES ($1, $2, $3)
RETURNING *;

-- name: UpdateBadgeLevel :one
UPDATE badges_acquired
SET level=$1
WHERE user_id=$2 AND badge_id=$3
RETURNING *;
