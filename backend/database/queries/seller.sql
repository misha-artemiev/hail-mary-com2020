-- name: GetSeller :one
SELECT users.user_id, email, seller_name, address_line1, address_line2, city, post_code, region, country, verified_by, verification_date
FROM sellers
INNER JOIN users ON sellers.user_id=users.user_od
WHERE users.user_id=?
LIMIT 1;

-- name: CreateSeller :execresult
INSERT INTO sellers (user_id, seller_name, address_line1, address_line2, city, post_code, region, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
