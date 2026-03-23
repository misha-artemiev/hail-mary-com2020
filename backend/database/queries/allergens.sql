-- name: GetBundleAllergens :many
SELECT a.allergen_id
FROM allergens a
JOIN bundle_allergens ba ON ba.allergen_id = a.allergen_id
JOIN bundles b ON b.bundle_id = ba.bundle_id
WHERE b.bundle_id=$1;

-- name: GetAllergens :many
SELECT *
FROM allergens;

-- name: CreateAllergen :one
INSERT INTO allergens (allergen_name)
VALUES ($1)
RETURNING *;

-- name: UpdateAllergen :one
UPDATE allergens
SET allergen_name = $2
WHERE allergen_id = $1
RETURNING *;

-- name: DeleteAllergen :one
DELETE FROM allergens
WHERE allergen_id = $1
RETURNING *;

-- name: AddBundlesAllergen :one
INSERT INTO bundle_allergens (bundle_id, allergen_id)
VALUES ($1,$2)
RETURNING *;

-- name: DeleteBundleAllergen :one
DELETE FROM bundle_allergens
WHERE allergen_id=$1 AND bundle_id=$2
RETURNING *;
