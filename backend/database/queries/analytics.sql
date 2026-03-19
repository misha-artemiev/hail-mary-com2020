-- name: GetGraphsTypes :many
SELECT *
FROM analytics_graphs_types;

-- name: GetGraphType :one
SELECT *
FROM analytics_graphs_types
WHERE graph_type_id=$1;

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

-- name: DeleteGraphSeries :exec
DELETE FROM analytics_series
WHERE graph_id=$1;

-- name: CreateGraphSeries :one
INSERT INTO analytics_series (graph_id, series_name, sort_index)
VALUES ($1, $2, $3)
RETURNING *;

-- name: CreateGraphPoint :one
INSERT INTO analytics_points (series_id, sort_index, x, y)
VALUES ($1, $2, $3, $4)
RETURNING *;

-- name: getGraphPoints :many
SELECT *
FROM analytics_points
WHERE series_id=$1;
