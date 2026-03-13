"""Constants for database lookup tables including categories and allergens."""

CATEGORIES = {
    1: "Bakery",
    2: "Produce",
    3: "Deli",
    4: "Prepared Meals",
    5: "Dairy",
    6: "Desserts",
    7: "Pantry",
    8: "Snacks",
}

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
