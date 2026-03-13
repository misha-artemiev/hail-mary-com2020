-- name: GetGraphsTypes :many
SELECT *
FROM analytics_graphs_types;

-- name: CreateGraph :one
INSERT INTO analytics_graphs (seller_id, graph_type)
VALUES ($1, $2)
RETURNING *;

-- name: GetGraph :one
SELECT *
FROM analytics_graphs
WHERE seller_id=$1 AND graph_type=$2
LIMIT 1;

-- name: GetGraphs :many
SELECT *
FROM analytics_graphs
WHERE seller_id=$1;

-- name: GetGraphSeries :many
SELECT *
FROM analytics_series
WHERE graph_id=$1
ORDER BY sort_index;

-- name: DeleteGraphSeries :many
DELETE FROM analytics_series
WHERE graph_id=$1
RETURNING *;

-- name: CreateGraphSeries :one
INSERT INTO analytics_series (graph_id, series_name, sort_index)
VALUES ($1, $2, $3)
RETURNING *;
