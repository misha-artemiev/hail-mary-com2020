import mysql
from mysql.connector import Error
from backend.internal.settings import Database_Settings

database_settings = Database_Settings()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=database_settings.host,
            port=database_settings.port,
            database=database_settings.database,
            user=database_settings.username,
            password=database_settings.password
        )
        if connection.is_connected():
            print("Connection to database successful.")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    

# User Table
def init_user_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(250) NOT NULL UNIQUE,
        pw_salt BINARY(16) NOT NULL,
        pw_hash BINARY(64) NOT NULL,
        role ENUM('seller','consumer','admin') NOT NULL DEFAULT 'consumer',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("User table initialized.")
    cursor.close()

# Consumer Table
def init_consumer_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS consumers (
        user_id INT NOT NULL,
        fName VARCHAR(100) NOT NULL,
        lName VARCHAR(100) NOT NULL,
        PRIMARY KEY (user_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Consumer table initialized.")
    cursor.close()

# Seller Table
def init_seller_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sellers (
        user_id INT NOT NULL,
        city VARCHAR(100) NOT NULL,
        seller_name VARCHAR(250) NOT NULL,
        verified_by INT,
        verification_date TIMESTAMP,
        PRIMARY KEY (user_id),
        FOREIGN KEY (verified_by) REFERENCES admins(user_id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Seller table initialized.")
    cursor.close()

#  Admin Table
def init_admin_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS admins (
        user_id INT NOT NULL,
        fName VARCHAR(100) NOT NULL,
        lName VARCHAR(100) NOT NULL,
        PRIMARY KEY (user_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Admin table initialized.")
    cursor.close()

# Bundle Table
def init_bundle_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS bundles (
        bundle_id INT AUTO_INCREMENT PRIMARY KEY,
        seller_id INT NOT NULL,
        category INT NOT NULL,
        description VARCHAR(255) NOT NULL,
        total_qty INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        discount_percentage INT NOT NULL,
        pickup_start_at TIMESTAMP NOT NULL,
        pickup_end_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category) REFERENCES food_category(category_id) ON DELETE SET NULL,
        FOREIGN KEY (seller_id) REFERENCES sellers(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Bundle table initialized.")
    cursor.close()

# Allergens Table
def init_allergens_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS allergens (
        allergen_id INT AUTO_INCREMENT PRIMARY KEY,
        allergen_name VARCHAR(100) NOT NULL UNIQUE   );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Allergens table initialized.")
    cursor.close()

# Bundle-Allergens Table
def init_bundle_allergens_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS bundle_allergens (
        bundle_id INT NOT NULL,
        allergen_id INT NOT NULL,
        PRIMARY KEY (bundle_id, allergen_id),
        FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
        FOREIGN KEY (allergen_id) REFERENCES allergens(allergen_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Bundle-Allergens table initialized.")
    cursor.close()

# Food Category Table
def init_food_category_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS food_category (
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(100) NOT NULL UNIQUE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Food Category table initialized.")
    cursor.close()

# Reservations Table
def init_reservation_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id INT AUTO_INCREMENT PRIMARY KEY,
        bundle_id INT NOT NULL,
        consumer_id INT,
        reserved_at TIMESTAMP,
        claim_code INT,
        status ENUM('available', 'reserved', 'collected', 'no_show', 'expired') NOT NULL DEFAULT 'available',
        collected_at TIMESTAMP,
        FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id),
        FOREIGN KEY (consumer_id) REFERENCES consumers(user_id)
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Reservations table initialized.")
    cursor.close()

# Badge Table
def init_badge_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS badges (
        badge_id INT AUTO_INCREMENT PRIMARY KEY,
        badge_name VARCHAR(100) NOT NULL UNIQUE,
        description VARCHAR(255) NOT NULL
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Badge table initialized.")
    cursor.close()

#  Badge_aquired Table
def init_badge_aquired_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS badge_aquired (
        user_id INT NOT NULL,
        badge_id INT NOT NULL,
        aquired_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, badge_id),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Badge_Aquired table initialized.")
    cursor.close()

# Issue Report Table
def init_issue_report_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS issue_reports (
        report_id INT AUTO_INCREMENT PRIMARY KEY,
        reporter_id INT NOT NULL,
        reported_bundle_id INT NOT NULL,
        issue_type ENUM(
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
        ) NOT NULL,
        issue_description VARCHAR(500) NOT NULL,
        reported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
        FOREIGN KEY (reporter_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (reported_bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Issue Report table initialized.")
    cursor.close()

# Token Table
def init_token_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tokens (
        token_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        token VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Token table initialized.")
    cursor.close()

# Inbox Table
def init_inbox_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS inbox (
        message_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        sender_id INT NOT NULL,
        message_subject VARCHAR(255) NOT NULL,
        message_text VARCHAR(1000) NOT NULL,
        sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        read_status BOOLEAN NOT NULL DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Inbox table initialized.")
    cursor.close()

# Forecast Input Table
def init_forecast_input_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS forecast_input (
        input_id INT AUTO_INCREMENT PRIMARY KEY,
        bundle_id INT NOT NULL,
        date DATE NOT NULL,
        day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
        pickup_start_hour INT NOT NULL,
        pickup_end_hour INT NOT NULL,
        is_holiday BOOLEAN NOT NULL,
        temperature DECIMAL(5,2) NOT NULL,
        weather_condition ENUM('sunny', 'cloudy', 'rainy', 'snowy', 'foggy') NOT NULL,
        observend_reservations INT NOT NULL,
        observed_no_shows INT NOT NULL,
        UNIQUE (bundle_id, date),
        FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Forecast Input table initialized.")
    cursor.close()

# Forecast Output Table
def init_forecast_output_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS forecast_output (
        output_id INT AUTO_INCREMENT PRIMARY KEY,
        bundle_id INT NOT NULL,
        predicted_reservations INT NOT NULL,
        predicted_no_show_prob INT NOT NULL,
        confidence DECIMAL(5,2) NOT NULL,
        rationale VARCHAR(500),
        generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Forecast Output table initialized.")
    cursor.close()

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        init_user_table(conn)
        init_consumer_table(conn)
        init_seller_table(conn)
        init_admin_table(conn)
        init_bundle_table(conn)
        init_allergens_table(conn)
        init_bundle_allergens_table(conn)
        init_food_category_table(conn)
        init_reservation_table(conn)
        init_badge_table(conn)
        init_badge_aquired_table(conn)
        init_issue_report_table(conn)
        init_token_table(conn)
        init_inbox_table(conn)  
        init_forecast_input_table(conn)
        init_forecast_output_table(conn)
        conn.close()    
        print("Database connection closed.")
