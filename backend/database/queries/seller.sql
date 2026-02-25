-- name: GetSeller :one
SELECT u.user_id, u.username, u.email, s.seller_name, s.address_line1, s.address_line2, s.city, s.post_code, s.region, s.country, s.verified_by, s.verification_date, u.last_login, u.created_at, s.latitude, s.longitude
FROM sellers s
INNER JOIN users u ON s.user_id=u.user_id
WHERE u.user_id=$1
LIMIT 1;

-- name: CreateSeller :one
INSERT INTO sellers (user_id, seller_name, address_line1, address_line2, city, post_code, region, country, latitude, longitude)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
RETURNING *;

-- name: GetSellerByLocation :many
SELECT u.user_id, u.username, u.email, s.seller_name, s.address_line1, s.address_line2, s.city, s.post_code, s.region, s.country, s.verified_by, s.verification_date, u.last_login, u.created_at, s.latitude, s.longitude
FROM sellers s
INNER JOIN users u ON s.user_id=u.user_id
WHERE s.latitude < sqlc.arg(lat_max) AND s.latitude > sqlc.arg(lat_min) AND s.longitude < sqlc.arg(lon_max) AND s.longitude > sqlc.arg(lon_min);
