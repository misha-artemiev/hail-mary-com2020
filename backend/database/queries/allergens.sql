-- name: GetBundleAllergens :many
SELECT a.allergen_id
FROM allergens a
JOIN bundle_allergens ba ON ba.allergen_id = a.allergen_id
JOIN bundles b ON b.bundle_id = ba.bundle_id
WHERE b.bundle_id=$1;
