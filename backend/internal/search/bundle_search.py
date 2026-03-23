"""Bundle search helpers."""

from internal.database.dependency import database_dependency
from internal.queries.allergens import AsyncQuerier as AllergensQuerier
from internal.queries.category import AsyncQuerier as CategoriesQuerier
from internal.queries.models import Bundle
from internal.queries.reservations import AsyncQuerier as ReservationQuerier


async def filter_bundle(
    conn: database_dependency,
    bundle: Bundle,
    allergens_filter: list[int] | None,
    categories_filter: list[int] | None,
    max_price: float | None,
) -> bool:
    """Check if a bundle passes all filters.

    Args:
        conn: database connection
        bundle: the bundle to check
        allergens_filter: list of allergen IDs to exclude
        categories_filter: list of category IDs to filter by
        max_price: maximum discounted price

    Returns:
        True if bundle passes all filters, False otherwise
    """
    allergens = [
        item
        async for item in AllergensQuerier(conn).get_bundle_allergens(
            bundle_id=bundle.bundle_id
        )
    ]
    if (
        allergens
        and allergens_filter
        and not set(allergens).isdisjoint(set(allergens_filter))
    ):
        return False

    categories = [
        item
        async for item in CategoriesQuerier(conn).get_bundle_categories(
            bundle_id=bundle.bundle_id
        )
    ]
    if (
        categories
        and categories_filter
        and set(categories).isdisjoint(set(categories_filter))
    ):
        return False

    if max_price and (bundle.price * bundle.discount_percentage / 100) > max_price:
        return False

    reservations = [
        item
        async for item in ReservationQuerier(conn).get_bundle_reservations(
            bundle_id=int(bundle.bundle_id)
        )
    ]
    return bool(reservations and bundle.total_qty > len(list(reservations)))
