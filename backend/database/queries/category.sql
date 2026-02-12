-- name: GetBundleCategories :many
SELECT c.category_id
FROM category c
JOIN bundle_category bc ON bc.category_id = c.category_id
JOIN bundles b ON b.bundle_id = bc.bundle_id
WHERE b.bundle_id=$1;
