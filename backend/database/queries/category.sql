-- name: GetBundleCategories :many
SELECT c.category_id
FROM category c
JOIN bundle_category bc ON bc.category_id = c.category_id
JOIN bundles b ON b.bundle_id = bc.bundle_id
WHERE b.bundle_id=$1;

-- name: GetCategories :many
SELECT *
FROM category;

-- name: GetCategory :one
SELECT *
FROM category
WHERE category_id=$1
LIMIT 1;

-- name: CreateCategory :one
INSERT INTO category (category_name, category_coefficient)
VALUES ($1, $2)
RETURNING *;

-- name: UpdateCategory :one
UPDATE category
SET category_name = $2, category_coefficient = $3
WHERE category_id = $1
RETURNING *;

-- name: DeleteCategory :one
DELETE FROM category
WHERE category_id = $1
RETURNING *;

-- name: AddBundlesCategory :one
INSERT INTO bundle_category (bundle_id, category_id)
VALUES ($1,$2)
RETURNING *;

-- name: DeleteBundleCategory :one
DELETE FROM bundle_category
WHERE category_id=$1 AND bundle_id=$2
RETURNING *;
