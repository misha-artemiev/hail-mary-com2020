"""Constants for database lookup tables including categories and allergens."""

CATEGORIES = [
    {"cat_id": 1, "name": "Bakery",         "coefficient": 1.5},  # bread ~1.4, cakes ~1.6-2.0
    {"cat_id": 2, "name": "Produce",        "coefficient": 0.9},  # veg 0.5–2, fruit 0.5–1.5
    {"cat_id": 3, "name": "Deli",           "coefficient": 6.5},  # pork 7–12, poultry 6–9, processed meats
    {"cat_id": 4, "name": "Prepared Meals", "coefficient": 3.5},  # mixed ingredients, varies by meat content
    {"cat_id": 5, "name": "Dairy",          "coefficient": 5.0},  # milk 3.15, yogurt ~3, cheese 13–21
    {"cat_id": 6, "name": "Drinks",         "coefficient": 0.9},  # juice ~0.5, beer ~1, wine ~1.4
    {"cat_id": 7, "name": "Pantry",         "coefficient": 2.5},  # pasta ~1.2, rice ~3.6, oils ~3–4
    {"cat_id": 8, "name": "Snacks",         "coefficient": 2.5},  # crisps ~2–3, biscuits ~2–3
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
