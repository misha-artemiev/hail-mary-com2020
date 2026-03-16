"""CO2e estimator for rescued food items."""

from statistics import mean


def estimate_carbon_doixide_saved(
    category_coefficients: list[float], weight_g: int
) -> int:
    """Return the estimated CO2e saved (g).

    Args:
        category_coefficients: The food category coefficients
        weight_g: bundle weight in grams

    Returns:
        estimated carbon dioxide saved.
    """
    coefficient = mean(category_coefficients)
    return int(weight_g * coefficient)
