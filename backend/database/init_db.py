from logging import getLogger
from logging.config import dictConfig
from pathlib import Path
from re import IGNORECASE, search, split

from internal.settings import database_settings
from psycopg import Connection, Error, connect
from uvicorn.config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = getLogger("uvicorn.info")
schema_path = Path("database/migrations/schema.sql")


def load_queries() -> list[str]:
    content = schema_path.read_text(encoding="utf-8")
    raw_queries = split(r"\n\s*\n", content)
    return [q.strip() for q in raw_queries if q.strip()]


table_queries = load_queries()


# Connect to the database
def get_db_connection() -> Connection | None:
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
    table_match = search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?", sql, IGNORECASE
    )
    if table_match:
        return ("TABLE", table_match.group(1))

    enum_match = search(r"CREATE\s+TYPE\s+`?(\w+)`?\s+AS\s+ENUM", sql, IGNORECASE)
    if enum_match:
        return ("ENUM", enum_match.group(1))
    return None


def create_all_tables(conn: Connection) -> None:
    for sql in table_queries:
        type_name = get_type_and_name(sql)
        if not type_name:
            logger.error("unrecognised entity type")
            continue
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                logger.info(f"{type_name[0].lower()} {type_name[1]} created.")
        except Error as err:
            logger.error(f"Failed to create {type_name[0]} {type_name[1]}: {err}")
        conn.commit()


def show_all_tables(conn: Connection) -> None:
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


def drop_all_tables(conn: Connection) -> None:
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
            cursor.execute(f"DROP {type_name[0]} IF EXISTS {type_name[1]};")
            logger.info(f"table {type_name[1]} removed.")
    conn.commit()


def main() -> None:
    conn = get_db_connection()
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
            create_all_tables(conn)
        case 2:
            # Show all tables
            show_all_tables(conn)
        case 3:
            # Drop all tables
            drop_all_tables(conn)
        case 4:
            logger.info("Shutting down: database connection closed")
    conn.close()
    logger.info("Database connection closed.")


if __name__ == "__main__":
    main()
