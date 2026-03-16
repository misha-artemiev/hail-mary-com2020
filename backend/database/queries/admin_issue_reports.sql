-- name: CreateAdminIssueReport :one
INSERT INTO admin_issue_reports (user_id, issue_type, description)
VALUES ($1, $2, $3)
RETURNING *;

-- name: GetAdminIssueReports :many
SELECT * FROM admin_issue_reports;

-- name: GetAdminIssueReportsByUser :many
SELECT * FROM admin_issue_reports
WHERE user_id = $1;

-- name: UpdateAdminIssueReportStatus :one
UPDATE admin_issue_reports
SET status = $2
WHERE report_id = $1
RETURNING *;

-- name: DeleteAdminIssueReport :one
DELETE FROM admin_issue_reports
WHERE report_id = $1
RETURNING *;
