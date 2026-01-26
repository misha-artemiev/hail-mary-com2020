from psycopg import connect, Error, Connection
from internal.settings import database_settings
from uvicorn.config import LOGGING_CONFIG
from logging.config import dictConfig
from logging import getLogger
from re import search, IGNORECASE

dictConfig(LOGGING_CONFIG)
logger = getLogger("uvicorn.info")
table_queries: list[str] = []

# Connect to the database
def get_db_connection() -> Connection | None:
    try:
        connection = connect(
            host=database_settings.host,
            port=database_settings.port,
            dbname=database_settings.database,
            user=database_settings.username,
            password=database_settings.password
        )
        if connection.closed == 0:
            logger.info("Connection to database successful.")
            return connection
    except Error as e:
        logger.error(f"Error while connecting to Postgres: {e}")
        return None
 
# Get entity name and type
def get_type_and_name(sql: str) -> tuple[str, str] | None:
    table_match = search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?", 
        sql, 
        IGNORECASE
    )
    if table_match:
        return ("TABLE", table_match.group(1))

    enum_match = search(
        r"CREATE\s+TYPE\s+`?(\w+)`?\s+AS\s+ENUM", 
        sql, 
        IGNORECASE
    )
    if enum_match:
        return ("ENUM", enum_match.group(1))
    return None

# Create user role enum
table_queries.append("""
CREATE TYPE user_role AS ENUM (
    'seller',
    'consumer',
    'admin'
);
""")

# Create reservation status enum
table_queries.append("""
CREATE TYPE reservation_status AS ENUM (
    'reserved',
    'collected',
    'no_show'
);
""")

# Create admin issue enum
table_queries.append("""
CREATE TYPE admin_issue_type AS ENUM (
    'LOGIN_FAILED',
    'ACCOUNT_LOCKED',
    'PASSWORD_RESET_FAILED',
    'PAYMENT_FAILED',
    'QR_CODE_NOT_GENERATED',
    'QR_CODE_SCAN_ERROR',
    'APP_CRASH',
    'DATA_INCONSISTENCY',
    'PERMISSION_ERROR',
    'OTHER'
);
""")

# Create seller issue enum
table_queries.append("""
CREATE TYPE seller_issue_type AS ENUM (
    'ITEM_MISSING',
    'ITEM_INCORRECT',
    'ITEM_DAMAGED',
    'SELLER_CLOSED',
    'SELLER_REFUSED_PICKUP',
    'PICKUP_DELAYED',
    'BUNDLE_EXPIRED',
    'RESERVATION_CANCELLED_BY_SELLER',
    'RESERVATION_NOT_FOUND',
    'CLAIM_CODE_INVALID',
    'CLAIM_CODE_ALREADY_USED',
    'OTHER'
);
""")

# Create issue status enum
table_queries.append("""
CREATE TYPE issue_status AS ENUM (
    'open',
    'in_progress',
    'closed'
);
""")

# Create day of the week enum
table_queries.append("""
CREATE TYPE day_of_week AS ENUM (
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
);
""")

# Create weather enum
table_queries.append("""
CREATE TYPE weather_flag AS ENUM (
    'sunny',
    'cloudy',
    'rainy',
    'snowy',
    'windy'
);
""")

# Create users table
table_queries.append("""
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(250) NOT NULL UNIQUE,
    pw_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'consumer',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""")

# Create consumers table
table_queries.append("""
CREATE TABLE IF NOT EXISTS consumers (
    user_id INT NOT NULL,
    fName VARCHAR(100) NOT NULL,
    lName VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create admins table
table_queries.append("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INT NOT NULL,
    fName VARCHAR(100) NOT NULL,
    lName VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create sellers table
table_queries.append("""
CREATE TABLE IF NOT EXISTS sellers (
    user_id INT NOT NULL,
    seller_name VARCHAR(255) NOT NULL,
    verified_by INT,
    verification_date TIMESTAMP,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    post_code VARCHAR(20) NOT NULL,
    region VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (verified_by) REFERENCES admins(user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create boundles table
table_queries.append("""
CREATE TABLE IF NOT EXISTS bundles (
    bundle_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL,
    bundle_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    total_qty INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discount_percentage INT NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(user_id) ON DELETE CASCADE
);
""")

# Create allergens table
table_queries.append("""
CREATE TABLE IF NOT EXISTS allergens (
    allergen_id SERIAL PRIMARY KEY,
    allergen_name VARCHAR(100) NOT NULL UNIQUE);
""")

# Create boundle allergens table
table_queries.append("""
CREATE TABLE IF NOT EXISTS bundle_allergens (
    bundle_id INT NOT NULL,
    allergen_id INT NOT NULL,
    PRIMARY KEY (bundle_id, allergen_id),
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergens(allergen_id) ON DELETE CASCADE
);
""")

# Create category table
table_queries.append("""
CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);
""")

# Create bundle category table
table_queries.append("""
CREATE TABLE IF NOT EXISTS bundle_category (
    category_id INT NOT NULL ,
    bundle_id INT NOT NULL,
    PRIMARY KEY (category_id, bundle_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE CASCADE,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
);
""")

# Create reservations table
table_queries.append("""
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    bundle_id INT NOT NULL,
    consumer_id INT NOT NULL,
    reserved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claim_code VARCHAR(20) NOT NULL,
    status reservation_status NOT NULL DEFAULT 'reserved',
    collected_at TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    FOREIGN KEY (consumer_id) REFERENCES consumers(user_id)
);
""")

# Create badges table
table_queries.append("""
CREATE TABLE IF NOT EXISTS badges (
    badge_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL
);
""")

# Create badges acquired table
table_queries.append("""
CREATE TABLE IF NOT EXISTS badges_acquired (
    user_id INT NOT NULL,
    badge_id INT NOT NULL,
    acquired_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
);
""")

# Create admin issue reports table
table_queries.append("""
CREATE TABLE IF NOT EXISTS admin_issue_reports (
    report_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    issue_type admin_issue_type NOT NULL,
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status issue_status NOT NULL DEFAULT 'open',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create seller issue reports table
table_queries.append("""
CREATE TABLE IF NOT EXISTS seller_issue_reports (
    report_id SERIAL PRIMARY KEY,
    reservation_id INT NOT NULL,
    issue_type seller_issue_type,
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status issue_status NOT NULL DEFAULT 'open',
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE
);
""")

# Create token table
table_queries.append("""
CREATE TABLE IF NOT EXISTS token (
    token_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create inbox table
table_queries.append("""
CREATE TABLE IF NOT EXISTS inbox (
    message_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    sender_id INT NOT NULL,
    message_subject VARCHAR(255) NOT NULL,
    message_text VARCHAR(1000) NOT NULL,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_status BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

# Create forcast input table
table_queries.append("""
CREATE TABLE IF NOT EXISTS forecast_input (
    input_id SERIAL PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    day_of_week day_of_week NOT NULL,
    window_start_hour TIME NOT NULL,
    window_end_hour TIME NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    weather_flag weather_flag NOT NULL,
    observed_reservations INT NOT NULL,
    observed_no_shows INT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(user_id) ON DELETE CASCADE
);
""")

# Create forcast output table
table_queries.append("""
CREATE TABLE IF NOT EXISTS forecast_output (
    output_id SERIAL PRIMARY KEY,
    bundle_id INT NOT NULL,
    predicted_reservations INT NOT NULL,
    predicted_no_show_prob DECIMAL(5,4) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    rationale VARCHAR(500),
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
);
""")

def main():
    conn = get_db_connection()
    if not conn:
        return
    option = 0
    while option not in (1,2,3,4):
        option = int(input("(1) Init all table, (2) Show all tables, (3) Drop all tables, (4) exit: "))
    if option == 4 or input(f"confirm option {option} (y/N): ") not in ("y","Y","yes"):
        conn.close()
        logger.info("Shutting down: database connection closed")
        return
    match option:
        case 1:
            # Create all tables
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
        case 2:
            # Show all tables
            with conn.cursor() as cursor:
                cursor.execute("""SELECT table_name
                                  FROM information_schema.tables
                                  WHERE table_schema NOT IN ('pg_catalog', 'information_schema');""")
                tables = cursor.fetchall()
                logger.info("Current tables in the database:")
                for table in tables:
                    logger.info(table)
        case 3:
            # Drop all tables
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
    conn.close()
    logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
