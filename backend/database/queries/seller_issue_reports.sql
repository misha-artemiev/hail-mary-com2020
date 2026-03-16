-- name: CreateSellerIssueReport :one
INSERT INTO seller_issue_reports (reservation_id, issue_type, description)
VALUES ($1, $2, $3)
RETURNING *;

-- name: GetSellerIssueReports :many
SELECT * FROM seller_issue_reports;

-- name: GetSellerIssueReportsByUser :many
SELECT r.* FROM seller_issue_reports r
JOIN reservations res ON r.reservation_id = res.reservation_id
WHERE res.consumer_id = $1;

-- name: UpdateSellerIssueReportStatus :one
UPDATE seller_issue_reports
SET status = $2
WHERE report_id = $1
RETURNING *;

-- name: DeleteSellerIssueReport :one
DELETE FROM seller_issue_reports
WHERE report_id = $1
RETURNING *;
