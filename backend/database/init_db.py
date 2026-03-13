"""Initialisation and deinitialisation of the database."""

from logging import Logger, getLogger
from logging.config import dictConfig
from pathlib import Path
from re import IGNORECASE, search, split
from string.templatelib import Template

from internal.settings.env import database_settings
from psycopg import Connection, Error, connect
from uvicorn.config import LOGGING_CONFIG

from database.db_constants import ALLERGENS, ANALYTICS_GRAPHS_TYPES, BADGES, CATEGORIES

dictConfig(LOGGING_CONFIG)
SCHEMA_PATH = Path("database/migrations/schema.sql")


def load_queries() -> list[str]:
    """Loads table creation queries from schema.

    Returns:
      list of separate queries
    """
    content = SCHEMA_PATH.read_text(encoding="utf-8")
    raw_queries = split(r"\n\s*\n", content)
    return [q.strip() for q in raw_queries if q.strip()]


# Connect to the database
def get_db_connection(logger: Logger) -> Connection | None:
    """Opens connection to the database.

    Args:
      logger: configured logger

    Returns:
      Opened connection
    """
    try:
        connection = connect(
            host=database_settings.host,
            port=database_settings.port,
            dbname=database_settings.database,
            user=database_settings.username,
            password=database_settings.password,
        )
        if connection.closed == 0:
            logger.info("Connection to database successful.")
            return connection
        logger.error("Connection is closed")
        return None
    except Error as e:
        logger.error(f"Error while connecting to Postgres: {e}")
        return None


# Get entity name and type
def get_type_and_name(sql: str) -> tuple[str, str] | None:
    """Extracts name and type of the entity from the query.

    Args:
        sql: sql string

    Returns:
      tuple with table type and name
    """
    table_match = search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?", sql, IGNORECASE
    )
    if table_match:
        return ("TABLE", table_match.group(1))

    enum_match = search(r"CREATE\s+TYPE\s+`?(\w+)`?\s+AS\s+ENUM", sql, IGNORECASE)
    if enum_match:
        return ("ENUM", enum_match.group(1))
    return None


def create_all_tables(
    logger: Logger, table_queries: list[str], conn: Connection
) -> None:
    """Execute sql for each table.

    Args:
      logger: configured logger
      table_queries: list of the queries for table craetion
      conn: connection to the database
    """
    for sql in table_queries:
        type_name = get_type_and_name(sql)
        if not type_name:
            logger.error("unrecognised entity type")
            continue
        try:
            with conn.cursor() as cursor:
                cursor.execute(Template(sql))
                logger.info(f"{type_name[0].lower()} {type_name[1]} created.")
        except Error as err:
            logger.error(f"Failed to create {type_name[0]} {type_name[1]}: {err}")
        conn.commit()


def show_all_tables(logger: Logger, conn: Connection) -> None:
    """Show all tables located in the database.

    Args:
      logger: configured logger
      conn: connection to the database
    """
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
        """)
        tables = cursor.fetchall()
        logger.info("Current tables in the database:")
        for table in tables:
            logger.info(table)


def drop_all_tables(logger: Logger, table_queries: list[str], conn: Connection) -> None:
    """Drops all created tables from database.

    Args:
      logger: configured logger
      table_queries: list of the queries for table craetion
      conn: connection to the database
    """
    table_queries.reverse()
    for sql in table_queries:
        type_name = get_type_and_name(sql)
        if not type_name:
            logger.error("unrecognised entity type")
            continue
        if type_name[0] == "ENUM":
            logger.warning(f"skipping {type_name[1]} as enum")
            continue
        with conn.cursor() as cursor:
            cursor.execute(Template(f"DROP {type_name[0]} IF EXISTS {type_name[1]};"))
            logger.info(f"table {type_name[1]} removed.")
    conn.commit()


def seed_static_data(logger: Logger, conn: Connection) -> None:
    """Inserts categories and allergens into the db."""
    try:
        # Seed Categories
        logger.info("inserting categories")
        for cat_id, name in CATEGORIES.items():
            conn.execute(
                "INSERT INTO category (category_id, category_name) "
                "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (cat_id, name),
            )

        # Seed Allergens
        logger.info("inserting allergens")
        for all_id, name in ALLERGENS.items():
            conn.execute(
                "INSERT INTO allergens (allergen_id, allergen_name)"
                "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (all_id, name),
            )
        # Seed Bundles
        logger.info("inserting badges")
        for badge in BADGES:
            conn.execute(
                "INSERT INTO badges (badge_id, name, description)"
                "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (badge["badge_id"], badge["name"], badge["description"]),
            )
        logger.info("inserting analytics graphs types")
        for graphs_types in ANALYTICS_GRAPHS_TYPES:
            conn.execute(
                "INSERT INTO analytics_graphs_types "
                "(graph_type_id, chart_type, graph_summary, x_axis_label, y_axis_label)"
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (graphs_types["graph_type_id"], graphs_types["chart_type"], graphs_types["graph_summary"], graphs_types["x_axis_label"], graphs_types["y_axis_label"]),
            )
        conn.commit()
        logger.info("finished inserting data")
    except Error as e:
        logger.error(f"Error seeding data: {e}")
        conn.rollback()


def main() -> None:
    """Entrypoint for database management script."""
    dictConfig(LOGGING_CONFIG)
    logger = getLogger("uvicorn.info")
    table_queries = load_queries()
    conn = get_db_connection(logger)
    if not conn:
        return
    option = 0
    while option not in {1, 2, 3, 4}:
        message = (
            "(1) Init all table, (2) Show all tables, (3) Drop all tables, (4) exit: "
        )
        option = int(input(message))
    if input(f"confirm option {option} (y/N): ") not in {"y", "Y", "yes"}:
        option = 0
    match option:
        case 1:
            # Create all tables
            create_all_tables(logger, table_queries, conn)
            seed_static_data(logger, conn)
        case 2:
            # Show all tables
            show_all_tables(logger, conn)
        case 3:
            # Drop all tables
            drop_all_tables(logger, table_queries, conn)
        case 4:
            logger.info("shutting down: database connection closed")
    conn.close()
    logger.info("database connection closed.")


if __name__ == "__main__":
    main()
