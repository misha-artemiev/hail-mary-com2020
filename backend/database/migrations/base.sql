CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(250) NOT NULL UNIQUE,
    pw_hash VARCHAR(255) NOT NULL,
    role ENUM('seller','consumer','admin') NOT NULL DEFAULT 'consumer',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consumers (
    user_id INT NOT NULL,
    fName VARCHAR(100) NOT NULL,
    lName VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

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

CREATE TABLE IF NOT EXISTS admins (
    user_id INT NOT NULL,
    fName VARCHAR(100) NOT NULL,
    lName VARCHAR(100) NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bundles (
    bundle_id INT AUTO_INCREMENT PRIMARY KEY,
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

CREATE TABLE IF NOT EXISTS allergens (
    allergen_id INT AUTO_INCREMENT PRIMARY KEY,
    allergen_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bundle_allergens (
    bundle_id INT NOT NULL,
    allergen_id INT NOT NULL,
    PRIMARY KEY (bundle_id, allergen_id),
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergens(allergen_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bundle_category (
    category_id INT NOT NULL ,
    bundle_id INT NOT NULL,
    PRIMARY KEY (category_id, bundle_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE CASCADE,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    bundle_id INT NOT NULL,
    consumer_id INT NOT NULL,
    reserved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claim_code VARCHAR(20) NOT NULL,
    status ENUM('reserved', 'collected', 'no_show') NOT NULL DEFAULT 'reserved',
    collected_at TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE,
    FOREIGN KEY (consumer_id) REFERENCES consumers(user_id)
);

CREATE TABLE IF NOT EXISTS badges (
    badge_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS badges_acquired (
    user_id INT NOT NULL,
    badge_id INT NOT NULL,
    acquired_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_issue_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    issue_type ENUM(
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
    ) NOT NULL,
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('open', 'in_progress', 'closed') NOT NULL DEFAULT 'open',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seller_issue_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL,
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
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('open', 'in_progress', 'closed') NOT NULL DEFAULT 'open',
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS token (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

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

CREATE TABLE IF NOT EXISTS forecast_input (
    input_id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    window_start_hour TIME NOT NULL,
    window_end_hour TIME NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    weather_flag ENUM('sunny', 'cloudy', 'rainy', 'snowy', 'windy') NOT NULL,
    observed_reservations INT NOT NULL,
    observed_no_shows INT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS forecast_output (
    output_id INT AUTO_INCREMENT PRIMARY KEY,
    bundle_id INT NOT NULL,
    predicted_reservations INT NOT NULL,
    predicted_no_show_prob DECIMAL(5,4) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    rationale VARCHAR(500),
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES bundles(bundle_id) ON DELETE CASCADE
);
