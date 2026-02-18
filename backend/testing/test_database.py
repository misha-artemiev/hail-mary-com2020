"""Test and init test database."""

from internal.database.manager import database_manager
from internal.settings.env import database_settings


def init_database() -> None:
    """Init connection to test database."""
    database_settings.model_construct(
        {"host", "port", "username", "password", "database"},
        host="127.0.0.1",
        port=5432,
        username="hail-mary",
        database="hail-mary",
        password="password",  # noqa: S106
    )
    database_manager.initialise()
