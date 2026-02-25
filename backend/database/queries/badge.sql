-- name: GetBadge :one
SELECT *
FROM badges
WHERE badge_id = $1
LIMIT 1;

-- name: GetConsumerBadges :many
SELECT b.badge_id, b.name, b.description, ba.acquired_at
FROM badges b
INNER JOIN badges_acquired ba ON ba.badge_id = b.badge_id
WHERE ba.user_id = $1;

-- name: GetBadges :many
SELECT *
FROM badges;
