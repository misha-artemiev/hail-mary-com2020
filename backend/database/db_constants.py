"""Constants for database lookup tables."""

from internal.queries.models import ChartType

CATEGORIES = [
    {"cat_id": 1, "name": "Bakery", "coefficient": 1},
    {"cat_id": 2, "name": "Produce", "coefficient": 1},
    {"cat_id": 3, "name": "Deli", "coefficient": 1},
    {"cat_id": 4, "name": "Prepared Meals", "coefficient": 1},
    {"cat_id": 5, "name": "Dairy", "coefficient": 1},
    {"cat_id": 6, "name": "Drinks", "coefficient": 1},
    {"cat_id": 7, "name": "Pantry", "coefficient": 1},
    {"cat_id": 8, "name": "Snacks", "coefficient": 1},
]

ALLERGENS = {1: "Gluten", 2: "Dairy", 3: "Nuts", 4: "Soy", 5: "Eggs", 6: "Sesame"}

BADGES = [
    {"badge_id": 1, "name": "Green Starter", "description": "Rescue your first meal"},
    {
        "badge_id": 2,
        "name": "Local Hero",
        "description": "Rescue from multiple different sellers",
    },
    {
        "badge_id": 3,
        "name": "Variety explorer",
        "description": "Rescue food from multiple categories",
    },
    {
        "badge_id": 4,
        "name": "Food Savior",
        "description": "Save food multiple days in a row",
    },
    {"badge_id": 5, "name": "Sweet Tooth", "description": "Save multiple desserts"},
    {
        "badge_id": 6,
        "name": "CO2 Cutter",
        "description": "Save significant amounts of CO2",
    },
    {
        "badge_id": 7,
        "name": "Right On Time",
        "description": "Consistently save meals without no-shows",
    },
]

ANALYTICS_GRAPHS_TYPES = [
    {
        "graph_type_id": 1,
        "chart_type": ChartType.MULTI_LINE,
        "graph_summary": "Weekly Sales vs Posted",
        "x_axis_label": "Timeline",
        "y_axis_label": "Reservations",
    },
    {
        "graph_type_id": 2,
        "chart_type": ChartType.PIE,
        "graph_summary": "Sell Through Rate",
        "x_axis_label": None,
        "y_axis_label": None,
    },
    {
        "graph_type_id": 3,
        "chart_type": ChartType.BAR,
        "graph_summary": "Category Distribution",
        "x_axis_label": None,
        "y_axis_label": "Reservations",
    },
    {
        "graph_type_id": 4,
        "chart_type": ChartType.BAR,
        "graph_summary": "Time Window Distribution",
        "x_axis_label": None,
        "y_axis_label": "Reservations",
    },
    {
        "graph_type_id": 5,
        "chart_type": ChartType.MULTI_LINE,
        "graph_summary": "Forecast vs Posted",
        "x_axis_label": "Bundle Date",
        "y_axis_label": "Quantity",
    },
]
