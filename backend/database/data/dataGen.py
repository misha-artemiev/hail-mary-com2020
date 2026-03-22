"""Generate random data for database.

Needs checks for attributes of the tables, I will double check but a triple
check would be good. I have added some comments to the code to explain what each
part is doing, but feel free to ask if you have any questions
if you need to understand.

This code generates synthetic data for the app although it is not perfect for the
final app, from my thoughts it is okay for the prototype and will be improves
later, remember for CW2 we have to make changes to almost every aspect of the app
so we can make improvements and get more realistic data therefore more marks for CW2.
"""

import asyncio
import io
import pathlib
import random
from datetime import UTC, datetime, timedelta
from secrets import SystemRandom
from typing import Any

import pandas as pd
from database.db_constants import ALLERGENS, BADGES, CATEGORIES
from faker import Faker
from fastapi import UploadFile
from fastapi.datastructures import Headers
from internal.auth.security import generate_claim_code, generate_token
from internal.block.management import BlockManagement

# setting the Faker library to use UK countries
fake = Faker("en_GB")

# meeting the requirements of the spec
NUM_SELLERS = 25
NUM_CONSUMERS = 50
NUM_ADMINS = 7
NUM_RESERVATIONS = 400
NUM_NO_SHOWS = 80
NUM_EXPIRIES = 50
NUM_REPORTS = 150
NUM_CATEGORIES = 6
NUM_PICKUP_WINDOWS = 10
WEEKS = 6
TOKEN_CREATION_THRESHOLD = 0.2
BADGE_PROBABILITY = 0.4
START_DATE = datetime.now(tz=UTC) - timedelta(days=15)

# default product category names (easily changeable if needed)
DEFAULT_CATEGORY_NAMES = [
    "Bakery",
    "Produce",
    "Deli",
    "Prepared Meals",
    "Dairy",
    "Drinks",
    "Pantry",
    "Snacks",
]

Faker.seed(42)
secure_rng = SystemRandom()


def generate_users() -> pd.DataFrame:
    """Creates the base user credentials and roles.

    then stores the users as a pandas dataframe
    via a list of dictionaries

    Returns:
      users dataframe
    """
    total_users = NUM_SELLERS + NUM_CONSUMERS + NUM_ADMINS
    roles = (
        ["seller"] * NUM_SELLERS + ["consumer"] * NUM_CONSUMERS + ["admin"] * NUM_ADMINS
    )

    users = []
    for i in range(1, total_users + 1):
        role = roles[i - 1]
        users.append({
            "user_id": i,
            "username": fake.unique.user_name(),
            "email": fake.unique.email(),
            "pw_hash": fake.sha256(),
            "role": role,
            "created_at": START_DATE - timedelta(days=secure_rng.randint(30, 100)),
            "last_login": START_DATE + timedelta(days=secure_rng.randint(0, 42)),
        })
    return pd.DataFrame(users)


def generate_profiles(
    users_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Creates profile tables with REAL UK COORDINATES for Sellers.

    Args:
      users_df: users dataframe

    Returns:
      tuples of sellers, consumers and admins
    """
    admin_ids = users_df[users_df["role"] == "admin"]["user_id"].tolist()

    exeter_data = [
        (50.7260, -3.5275, "EX4 3HG"),  # High St
        (50.7255, -3.5298, "EX4 3HP"),  # Guildhall
        (50.7238, -3.5321, "EX4 3AN"),  # Fore St
        (50.7272, -3.5235, "EX4 6NN"),  # Sidwell St
        (50.7295, -3.5330, "EX4 3RP"),  # Queen St
        (50.7198, -3.5268, "EX2 4AN"),  # The Quayside
        (50.7185, -3.5280, "EX2 8GT"),  # Piazza Terracina
        (50.7365, -3.5351, "EX4 4QJ"),  # University (Forum)
        (50.7330, -3.5360, "EX4 4RN"),  # University (Innovation)
        (50.7215, -3.5180, "EX2 4TA"),  # Magdalen Rd
        (50.7248, -3.5042, "EX1 2QN"),  # Heavitree Fore St
        (50.7255, -3.4980, "EX1 2RG"),  # Heavitree Tesco
        (50.7065, -3.5215, "EX2 8QF"),  # Marsh Barton
        (50.7090, -3.5240, "EX2 8LB"),  # Marsh Barton Sainsbury
        (50.7130, -3.5110, "EX2 5DW"),  # Wonford
        (50.7230, -3.4850, "EX4 8AD"),  # Whipton
        (50.7420, -3.5050, "EX4 8LL"),  # Pinhoe
        (50.7550, -3.4750, "EX2 7LL"),  # Sowton Ind Est
        (50.7160, -3.4800, "EX2 7HY"),  # Rydon Lane
        (50.7050, -3.4900, "EX2 7BY"),  # Countess Wear
        (50.7280, -3.5450, "EX4 4KU"),  # St Davids
        (50.7200, -3.5420, "EX4 1AH"),  # Exe Bridges
        (50.7290, -3.5200, "EX4 6LG"),  # Old Tiverton Rd
        (50.7150, -3.5350, "EX2 8DP"),  # Haven Banks
        (50.7320, -3.5100, "EX4 7AY"),  # Polsloe
    ]

    # Sellers
    sellers = []
    seller_ids = users_df[users_df["role"] == "seller"]["user_id"].tolist()

    for user_id, (lat, lon, pcode) in zip(seller_ids, exeter_data):
        sellers.append({
            "user_id": user_id,
            "seller_name": fake.company(),
            "verified_by": secure_rng.choice(admin_ids),
            "verification_date": START_DATE - timedelta(days=15),
            "address_line1": fake.street_address(),
            "city": "Exeter",
            "latitude": lat,
            "longitude": lon,
            "post_code": pcode,
            "country": "United Kingdom",
        })

    # consumers
    consumers = []
    consumer_ids = users_df[users_df["role"] == "consumer"]["user_id"].tolist()
    for uid in consumer_ids:
        consumers.append({
            "user_id": uid,
            "fname": fake.first_name(),
            "lname": fake.last_name(),
        })

    # admins
    admins = []
    admin_names = {
        "Muhammed": "Panjwani",
        "Massimo": "Belmonte",
        "Thomas": "Noakes",
        "Noé": "Bouchard",
        "Misha": "Artemiev",
        "Furkan": "Yalcintepe",
        "Ed": "Brown",
    }
    for userid, (first, last) in zip(admin_ids, admin_names.items()):
        admins.append({"user_id": userid, "fname": first, "lname": last})

    return pd.DataFrame(sellers), pd.DataFrame(consumers), pd.DataFrame(admins)


def generate_inventory(seller_ids: list[int], windows_df: pd.DataFrame) -> pd.DataFrame:
    """Makes 2 bundles for each seller every day, using pre-defined pickup windows.

    Args:
      seller_ids: list of sellers ids
      windows_df: dataframe of pickup windows (e.g. 8-9, 9-10)

    Returns:
      dataframe of bundles
    """
    # Convert dataframe to a list of dictionaries for easier random selection
    window_records = windows_df.to_dict("records")

    bundles = []
    bundle_id = 1

    for day in range(WEEKS * 7):
        current_date = START_DATE + timedelta(days=day)

        for seller_id in seller_ids:
            for _ in range(2):
                # Randomly select one of the defined pickup slots
                selected_window = secure_rng.choice(window_records)

                # Set Pickup Date (The Next Day)
                pickup_date = current_date + timedelta(days=1)

                # Create datetime objects for the window start/end
                win_start = pickup_date.replace(
                    hour=selected_window["window_start"],
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                win_end = pickup_date.replace(
                    hour=selected_window["window_end"],
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                # Simulated preferred collection-time label for analytics (nullable).

                # Set Listing Time (Evening of the current day, e.g., 4PM-8PM)
                # This ensures the item is listed BEFORE the pickup window starts
                closing_hour = secure_rng.randint(16, 20)
                created_at = current_date.replace(
                    hour=closing_hour,
                    minute=secure_rng.randint(0, 59),
                    second=0,
                    microsecond=0,
                )

                bundles.append({
                    "bundle_id": bundle_id,
                    "seller_id": seller_id,
                    "bundle_name": f"Surplus {fake.word().capitalize()} Bag",
                    "carbon_dioxide": round(secure_rng.randint(500, 8000), 2),
                    "description": fake.sentence(nb_words=10),
                    "total_qty": secure_rng.randint(1, 4),
                    "price": round(secure_rng.uniform(3.00, 7.50), 2),
                    "discount_percentage": secure_rng.choice([50, 60, 70]),
                    # Using the specific window times
                    "window_start": win_start,
                    "window_end": win_end,
                    "created_at": created_at,
                })
                bundle_id += 1

    return pd.DataFrame(bundles)


def generate_pickup_windows() -> pd.DataFrame:
    """Creates a list of pickup time windows.

    from 8am in 2 hour increments for the 10 windows

    Returns:
        dataframe of pickup windows
    """
    windows = []
    start_hour = 8
    for i in range(NUM_PICKUP_WINDOWS):
        windows.append({
            "window_start": start_hour + i,
            "window_end": start_hour + i + 2,
        })
    return pd.DataFrame(windows)


def generate_reservations(
    bundles_df: pd.DataFrame, consumers_df: pd.DataFrame
) -> pd.DataFrame:
    """Creates reservations with collected, no-show, and expired (reserved) states.

    Args:
      bundles_df: dataframe of bundles
      consumers_df: dataframe of consumers

    Returns:
      dataframe of reservations
    """
    statuses = (
        ["no_show"] * NUM_NO_SHOWS
        + ["reserved"] * NUM_EXPIRIES
        + ["collected"] * (NUM_RESERVATIONS - NUM_NO_SHOWS - NUM_EXPIRIES)
    )
    random.shuffle(statuses)

    reservations = []
    # create a list of bundle records from the bundles dataframe
    bundle_records = bundles_df.to_dict("records")
    # create a list of consumer ids from the consumers dataframe
    consumer_ids = consumers_df["user_id"].tolist()

    for reservation_id, status in enumerate(statuses, start=1):
        bundle = secure_rng.choice(bundle_records)
        reserved_at = bundle["window_start"] - timedelta(
            hours=secure_rng.randint(1, 24)
        )
        if reserved_at > bundle["window_end"]:
            reserved_at = bundle["window_start"]

        if status == "collected":
            window_minutes = int(
                (bundle["window_end"] - bundle["window_start"]).total_seconds() / 60
            )
            collected_at = bundle["window_start"] + timedelta(
                minutes=secure_rng.randint(10, max(10, window_minutes))
            )
        else:
            collected_at = None

        code = generate_claim_code([])

        reservations.append({
            "reservation_id": reservation_id,
            "bundle_id": bundle["bundle_id"],
            "consumer_id": secure_rng.choice(consumer_ids),
            "reserved_at": reserved_at,
            "claim_code": code,
            "collected_at": collected_at,
        })

    return pd.DataFrame(reservations)


def generate_issue_reports(
    reservations_df: pd.DataFrame, users_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Creates seller and admin issue reports.

    Args:
      reservations_df: dataframe of reservations
      users_df: dataframe of users

    Returns:
      dataframe of reservation issues
    """
    seller_issue_types = [
        "ITEM_MISSING",
        "ITEM_INCORRECT",
        "ITEM_DAMAGED",
        "SELLER_CLOSED",
        "SELLER_REFUSED_PICKUP",
        "PICKUP_DELAYED",
        "BUNDLE_EXPIRED",
        "RESERVATION_CANCELLED_BY_SELLER",
        "RESERVATION_NOT_FOUND",
        "CLAIM_CODE_INVALID",
        "CLAIM_CODE_ALREADY_USED",
        "OTHER",
    ]
    admin_issue_types = [
        "LOGIN_FAILED",
        "ACCOUNT_LOCKED",
        "PASSWORD_RESET_FAILED",
        "PAYMENT_FAILED",
        "APP_CRASH",
        "DATA_INCONSISTENCY",
        "PERMISSION_ERROR",
        "OTHER",
    ]
    statuses = ["open", "in_progress", "closed"]
    # split the reports into seller and admin reports (70 % seller, 30 % admin)
    seller_reports_count = int(NUM_REPORTS * 0.7)
    admin_reports_count = NUM_REPORTS - seller_reports_count

    reservation_ids = reservations_df["reservation_id"].tolist()
    user_ids = users_df["user_id"].tolist()

    seller_reports = []
    for report_id in range(1, seller_reports_count + 1):
        seller_reports.append({
            "report_id": report_id,
            "reservation_id": secure_rng.choice(reservation_ids),
            "issue_type": secure_rng.choice(seller_issue_types),
            # random realistic sentence (to be improved)
            "description": fake.sentence(nb_words=12),
            "created_at": START_DATE
            + timedelta(days=secure_rng.randint(0, WEEKS * 7 - 1)),
            "status": secure_rng.choice(statuses),
        })

    admin_reports = []
    for report_id in range(1, admin_reports_count + 1):
        admin_reports.append({
            "report_id": report_id,
            "user_id": secure_rng.choice(user_ids),
            "issue_type": secure_rng.choice(admin_issue_types),
            # random realistic sentence (to be improved)
            "description": fake.sentence(nb_words=12),
            "created_at": START_DATE
            + timedelta(days=secure_rng.randint(0, WEEKS * 7 - 1)),
            "status": secure_rng.choice(statuses),
        })

    return pd.DataFrame(seller_reports), pd.DataFrame(admin_reports)


def generate_inbox(users_df: pd.DataFrame) -> pd.DataFrame:
    """Generates welcome messages and system notifications.

    Args:
      users_df: dataframe of users

    Returns:
      dataframe of inbox messages
    """
    user_ids = users_df["user_id"].tolist()
    messages = []
    for i in range(1, 101):  # 100 sample messages
        recip = secure_rng.choice(user_ids)
        messages.append({
            "message_id": i,
            "user_id": recip,
            "sender_id": 1,  # assuming user_id 1 is the system/admin
            "message_subject": "Welcome to the App!",
            "message_text": fake.paragraph(nb_sentences=3),
            "sent_at": START_DATE + timedelta(days=secure_rng.randint(0, 30)),
            "read_status": secure_rng.choice([True, False]),
        })
    return pd.DataFrame(messages)


def generate_badges(consumers_df: pd.DataFrame) -> pd.DataFrame:
    """Creates base badge definitions and assigns tiered levels to consumers.

    Args:
      consumers_df: dataframe of consumers

    Returns:
      joining user-badge dataframe
    """
    # mapping badge id to max level
    badge_max_levels = {1: 1, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3}

    acquired = []
    consumer_ids = consumers_df["user_id"].tolist()

    for userid in consumer_ids:
        if secure_rng.random() < BADGE_PROBABILITY:
            # Picks 1 to 2 random base badges per user
            num_categories = secure_rng.randint(1, 2)
            chosen_badges = random.sample(BADGES, num_categories)

            for badge in chosen_badges:
                b_id = int(str(badge["badge_id"]))
                max_level = badge_max_levels[b_id]

                # Pick the highest level the user achieved in this category
                achieved_level = secure_rng.randint(1, max_level)

                # Calculate the total simulated time to reach this level
                # Base 1-40 days for Level 1, plus 2-14 days for every level after that
                progression_days = sum(
                    secure_rng.randint(2, 14) for _ in range(1, achieved_level)
                )
                start_offset = secure_rng.randint(1, 40)

                acquired_date = START_DATE + timedelta(
                    days=start_offset + progression_days
                )

                # Append ONLY the highest achieved level
                acquired.append({
                    "user_id": userid,
                    "badge_id": b_id,
                    "level": achieved_level,
                    "acquired_at": acquired_date,
                })

    return pd.DataFrame(acquired)


def generate_bundle_categories(bundles_df: pd.DataFrame) -> pd.DataFrame:
    """Links each bundle to 1-2 random category IDs from constants.

    Args:
        bundles_df: Dataframe containing bundle IDs.

    Returns:
        Dataframe representing the junction table.
    """
    bundle_ids = bundles_df["bundle_id"].tolist()
    category_ids = [category["cat_id"] for category in CATEGORIES]
    links = []

    for bundle_id in bundle_ids:
        selected = secure_rng.sample(category_ids, secure_rng.randint(1, 2))
        for cat_id in selected:
            links.append({"bundle_id": bundle_id, "category_id": cat_id})

    return pd.DataFrame(links)


def generate_bundle_allergens(bundles_df: pd.DataFrame) -> pd.DataFrame:
    """Links each bundle to 0-3 random allergen IDs from constants.

    Args:
        bundles_df: Dataframe containing bundle IDs.

    Returns:
        Dataframe representing the junction table.
    """
    bundle_ids = bundles_df["bundle_id"].tolist()
    allergen_ids = list(ALLERGENS.keys())
    links = []

    for bundle_id in bundle_ids:
        selected = secure_rng.sample(allergen_ids, secure_rng.randint(0, 3))
        for all_id in selected:
            links.append({"bundle_id": bundle_id, "allergen_id": all_id})

    return pd.DataFrame(links)


def generate_tokens(users_df: pd.DataFrame) -> pd.DataFrame:
    """Generates auth tokens for the token table.

    Args:
      users_df: dataframe of users

    Returns:
      dataframe of tokens
    """
    tokens: list[dict[str, Any]] = []
    for user_id in users_df["user_id"]:
        if (secure_rng.random()) > TOKEN_CREATION_THRESHOLD:
            created = START_DATE + timedelta(days=secure_rng.randint(1, 40))
            tokens.append({
                "token_id": len(tokens) + 1,
                "user_id": user_id,
                "token": generate_token(),
                "created_at": created,
                "expires_at": created + timedelta(hours=24),
            })
    return pd.DataFrame(tokens)


async def _upload_images() -> None:
    total = len(df_bundles)
    for i, bundle_id in enumerate(df_bundles["bundle_id"], start=1):
        name, content = secure_rng.choice(image_data)
        file = UploadFile(
            filename=name,
            file=io.BytesIO(content),
            headers=Headers({"content-type": "image/jpeg"}),
        )
        await block_management.upload_bundle_image(bundle_id, file)
        print(f"   Uploading images: {i}/{total}", end="\r")


# main execution
if __name__ == "__main__":
    print("Starting Data Gen...")

    OUTPUT_FOLDER = "synthetic_data"
    if not pathlib.Path(OUTPUT_FOLDER).exists():
        pathlib.Path(OUTPUT_FOLDER).mkdir(parents=True)
        print(f"Created folder: {OUTPUT_FOLDER}")

    bundle_images_path = pathlib.Path(__file__).parent / "bundle_images"
    bundle_images = list(bundle_images_path.glob("*.jpeg"))
    block_management = BlockManagement()
    block_management.initialise()

    df_users = generate_users()
    df_sellers, df_consumers, df_admins = generate_profiles(df_users)
    print(f"   Generated {len(df_users)} users")

    df_windows = generate_pickup_windows()

    df_bundles = generate_inventory(df_sellers["user_id"].tolist(), df_windows)

    image_data: list[tuple[str, bytes]] = [
        (img.name, img.read_bytes()) for img in bundle_images
    ]

    print(f"   Uploading {len(df_bundles)} bundle images...")
  #  asyncio.run(_upload_images())
    print()

    # Junction Tables
    df_bundle_cats = generate_bundle_categories(df_bundles)
    df_bundle_alls = generate_bundle_allergens(df_bundles)
    print(f"   Generated {len(df_bundles)} bundles")

    # reservations with different states (collected, no-show, expired)
    df_reservations = generate_reservations(df_bundles, df_consumers)
    print(f"   Generated {len(df_reservations)} reservations")

    # support and game
    df_seller_reports, df_admin_reports = generate_issue_reports(
        df_reservations, df_users
    )
    df_inbox = generate_inbox(df_users)
    df_badges_acquired = generate_badges(df_consumers)
    df_tokens = generate_tokens(df_users)

    # saving
    all_dfs = {
        "users": df_users,
        "sellers": df_sellers,
        "consumers": df_consumers,
        "admins": df_admins,
        "bundles": df_bundles,
        "bundle_category": df_bundle_cats,
        "bundle_allergens": df_bundle_alls,
        "reservations": df_reservations,
        "seller_issue_reports": df_seller_reports,
        "admin_issue_reports": df_admin_reports,
        "inbox": df_inbox,
        "badges_acquired": df_badges_acquired,
        "token": df_tokens,
    }

    print("Saving files...")
    for name, df in all_dfs.items():
        file_path = pathlib.Path(OUTPUT_FOLDER) / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"   - Saved {file_path}")

    print("Data Gen done yippee hurray")
