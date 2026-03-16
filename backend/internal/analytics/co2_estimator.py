"""CO2e estimator for rescued food items.

Methodology
-----------
Estimated CO2e saved = weight_kg x emission_factor_kg_co2e_per_kg

Emission factors are taken from:
  Poore, J., & Nemecek, T. (2018). "Reducing food's environmental impacts
  through producers and consumers." Science, 360(6392), 987-992.
  https://doi.org/10.1126/science.aaq0216

Visualised and verified against:
  Ritchie, H. & Roser, M. (2020). "Environmental impacts of food production."
  Our World in Data. https://ourworldindata.org/environmental-impacts-of-food

Category relevance informed by:
  WRAP (2021). "Food surplus and waste in the UK - key facts."
  https://wrap.org.uk/resources/report/food-surplus-and-waste-uk-key-facts

This is an MVP approximation, not a certified Life Cycle Assessment (LCA).
Factors represent global medians across production systems and should be
disclosed as rough estimates in any user-facing copy.
"""

from __future__ import annotations

from enum import StrEnum

# ---------------------------------------------------------------------------
# Emission factors (kgCO2e per kg of product)
# Source: Poore & Nemecek (2018) via Our World in Data (2020)
# ---------------------------------------------------------------------------


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


# kgCO2e per kg of rescued product.
# Notes per category:
#   BEEF_AND_LAMB      — Beef herd median 59.6; lamb 24.5. Beef used as
#                        upper-bound proxy for the combined ruminant category.
#                        Source: Poore & Nemecek (2018).
#   PORK               — Source: Poore & Nemecek (2018).
#   POULTRY            — Chicken retail median. Turkey similar; duck slightly
#                        higher. Source: Poore & Nemecek (2018).
#   FISH_AND_SEAFOOD   — High within-category range (wild ~3, farmed salmon
#                        ~11.9, tilapia ~3.1). 5.0 is a mid-range proxy.
#                        Source: Poore & Nemecek (2018). Low confidence.
#   DAIRY              — Cheese (hard/soft blend) 21.2; milk 3.2; yogurt ~3.3.
#                        This factor applies to solid cheese items. Use MILK
#                        sub-factor (3.2) for liquid milk / yogurt if the item
#                        can be identified. Source: Poore & Nemecek (2018).
#   EGGS               — Hen eggs retail. Source: Poore & Nemecek (2018).
#   BREAD_AND_PLAIN_BAKERY
#                      — Wheat bread retail. Wheat flour ~1.6; bread slightly
#                        lower after processing. WRAP (2021) identifies bread
#                        as the single largest rescued-food category by volume.
#                        Source: Poore & Nemecek (2018).
#   PASTRIES_AND_ENRICHED_BAKERY
#                      — No direct Poore & Nemecek factor. Composite proxy
#                        derived from ingredient-level factors: butter ~9,
#                        flour ~1.6, eggs ~4.5, sugar ~1.0. Recipe-weighted
#                        central estimate. Low confidence — disclose as
#                        approximation. Source: constituent factors from
#                        Poore & Nemecek (2018).
#   PREPARED_MEALS     — Rule-based composite (see estimate_co2e_saved).
#                        No single authoritative source; constituent-based
#                        from Poore & Nemecek (2018). Low confidence.
#   FRUIT_VEG_AND_SALADS
#                      — Blended midpoint: root veg ~0.4, tomatoes ~1.4,
#                        leafy veg ~0.3, bananas ~0.7, citrus ~0.4.
#                        Use 1.0 for hothouse/greenhouse produce where known.
#                        Source: Poore & Nemecek (2018).

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
