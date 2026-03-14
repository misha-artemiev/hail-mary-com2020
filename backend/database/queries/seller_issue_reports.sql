-- name: GetSellerIssueReports :many
SELECT * FROM seller_issue_reports;

-- name: UpdateSellerIssueReportStatus :one
UPDATE seller_issue_reports
SET status = $2
WHERE report_id = $1
RETURNING *;

-- name: DeleteSellerIssueReport :one
DELETE FROM seller_issue_reports
WHERE report_id = $1
RETURNING *;
