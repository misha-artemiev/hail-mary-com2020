-- name: GetAdminIssueReports :many
SELECT * FROM admin_issue_reports;

-- name: UpdateAdminIssueReportStatus :one
UPDATE admin_issue_reports
SET status = $2
WHERE report_id = $1
RETURNING *;

-- name: DeleteAdminIssueReport :one
DELETE FROM admin_issue_reports
WHERE report_id = $1
RETURNING *;
