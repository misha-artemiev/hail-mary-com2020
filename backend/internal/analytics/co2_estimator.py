"""CO2e estimator for rescued food items."""

from __future__ import annotations

from enum import StrEnum

class FoodCategory(StrEnum):
    """Food categories used for CO2e emission factors (Poore & Nemecek 2018)."""

    BEEF_AND_LAMB = "beef_and_lamb"
    PORK = "pork"
    POULTRY = "poultry"
    FISH_AND_SEAFOOD = "fish_and_seafood"
    DAIRY = "dairy"
    EGGS = "eggs"
    BREAD_AND_PLAIN_BAKERY = "bread_and_plain_bakery"
    PASTRIES_AND_ENRICHED_BAKERY = "pastries_and_enriched_bakery"
    PREPARED_MEALS = "prepared_meals"
    FRUIT_VEG_AND_SALADS = "fruit_veg_and_salads"

EMISSION_FACTORS: dict[FoodCategory, float] = {
    FoodCategory.BEEF_AND_LAMB: 60.0,
    FoodCategory.PORK: 7.6,
    FoodCategory.POULTRY: 6.0,
    FoodCategory.FISH_AND_SEAFOOD: 5.0,
    FoodCategory.DAIRY: 21.2,
    FoodCategory.EGGS: 4.5,
    FoodCategory.BREAD_AND_PLAIN_BAKERY: 1.4,
    FoodCategory.PASTRIES_AND_ENRICHED_BAKERY: 3.5,
    FoodCategory.PREPARED_MEALS: 4.0,  # default; see sub-tiers below
    FoodCategory.FRUIT_VEG_AND_SALADS: 0.7,
}

# Sub-tier factors for prepared meals when more detail is available.
# Source: constituent-based composite from Poore & Nemecek (2018).
PREPARED_MEAL_FACTORS: dict[str, float] = {
    "beef_lamb_based": 6.0,
    "chicken_pork_based": 4.0,
    "fish_based": 3.5,
    "vegetarian": 2.5,
    "vegan": 1.5,
    "unknown": 4.0,  # fallback
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def estimate_co2e_saved(
    category: FoodCategory,
    weight_kg: float,
    *,
    prepared_meal_subtype: str | None = None,
) -> float:
    """Return the estimated CO2e saved (kg) by rescuing one food item.

    Formula
    -------
        CO2e_saved = weight_kg x emission_factor_kgCO2e_per_kg

    Args:
        category: The food category of the rescued item.
        weight_kg: Weight of the item in kilograms. Use
            ``get_default_weight_kg`` if the exact weight is unknown.
        prepared_meal_subtype: Only relevant when ``category`` is
            ``PREPARED_MEALS``. One of: "beef_lamb_based",
            "chicken_pork_based", "fish_based", "vegetarian", "vegan",
            "unknown". Defaults to "unknown" (factor: 4.0 kgCO2e/kg).

    Returns:
        Estimated kgCO2e saved, rounded to four decimal places.

    Raises:
        ValueError: If ``weight_kg`` is negative.
    """
    if weight_kg < 0:
        raise ValueError(f"weight_kg must be non-negative, got {weight_kg}")

    if category is FoodCategory.PREPARED_MEALS:
        subtype = prepared_meal_subtype or "unknown"
        factor = PREPARED_MEAL_FACTORS.get(subtype, PREPARED_MEAL_FACTORS["unknown"])
    else:
        factor = EMISSION_FACTORS[category]

    return round(weight_kg * factor, 4)
