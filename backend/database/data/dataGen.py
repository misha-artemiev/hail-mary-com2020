'''Needs checks for attributes of the tables, I will double check but a triple check would be good.
I have added some comments to the code to explain what each part is doing, but feel free to
ask if you have any questions if you need to understand.'''

'''This code generates synthetic data for the app although it is not perfect for the final app,
from my thoughts it is okay for the prototype and will be improves later, remember for CW2 we have to
make changes to almost every aspect of the app so we can make improvements and get more realistic data 
therefore more marks for CW2.'''

import os
import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta
from faker import Faker

#setting the Faker library to use UK countries
fake = Faker('en_GB')

#meeting the requirements of the spec
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
#random start date can be changed
START_DATE = datetime(2024, 1, 1)

#default product category names (easily changeable if needed)
DEFAULT_CATEGORY_NAMES = [
    'Bakery',
    'Produce',
    'Deli',
    'Prepared Meals',
    'Dairy',
    'Drinks',
    'Pantry',
    'Snacks'
]

random.seed(42)
np.random.seed(42)
Faker.seed(42)

def generate_users():
    """creates the base user credentials and roles. then stores the users as a pandas dataframe
        via a list of dictionaries """
    total_users = NUM_SELLERS + NUM_CONSUMERS + NUM_ADMINS
    roles = (['seller'] * NUM_SELLERS + 
             ['consumer'] * NUM_CONSUMERS + 
             ['admin'] * NUM_ADMINS)
    
    users = []
    for i in range(1, total_users + 1):
        role = roles[i-1]
        users.append({
            'user_id': i,
            'email': fake.unique.email(),
            'pw_hash': fake.sha256(),
            'role': role,
            'created_at': START_DATE - timedelta(days=random.randint(30, 100)),
            'last_login': START_DATE + timedelta(days=random.randint(0, 42))
        })
    return pd.DataFrame(users)

def generate_profiles(users_df):
    """Creates profile tables with REAL UK COORDINATES for Sellers."""
    admin_ids = users_df[users_df['role'] == 'admin']['user_id'].tolist()
    
    exeter_data = [
        (50.7260, -3.5275, "EX4 3HG"), # High St
        (50.7255, -3.5298, "EX4 3HP"), # Guildhall
        (50.7238, -3.5321, "EX4 3AN"), # Fore St
        (50.7272, -3.5235, "EX4 6NN"), # Sidwell St
        (50.7295, -3.5330, "EX4 3RP"), # Queen St
        (50.7198, -3.5268, "EX2 4AN"), # The Quayside
        (50.7185, -3.5280, "EX2 8GT"), # Piazza Terracina
        (50.7365, -3.5351, "EX4 4QJ"), # University (Forum)
        (50.7330, -3.5360, "EX4 4RN"), # University (Innovation)
        (50.7215, -3.5180, "EX2 4TA"), # Magdalen Rd
        (50.7248, -3.5042, "EX1 2QN"), # Heavitree Fore St
        (50.7255, -3.4980, "EX1 2RG"), # Heavitree Tesco
        (50.7065, -3.5215, "EX2 8QF"), # Marsh Barton
        (50.7090, -3.5240, "EX2 8LB"), # Marsh Barton Sainsbury
        (50.7130, -3.5110, "EX2 5DW"), # Wonford
        (50.7230, -3.4850, "EX4 8AD"), # Whipton
        (50.7420, -3.5050, "EX4 8LL"), # Pinhoe
        (50.7550, -3.4750, "EX2 7LL"), # Sowton Ind Est
        (50.7160, -3.4800, "EX2 7HY"), # Rydon Lane
        (50.7050, -3.4900, "EX2 7BY"), # Countess Wear
        (50.7280, -3.5450, "EX4 4KU"), # St Davids
        (50.7200, -3.5420, "EX4 1AH"), # Exe Bridges
        (50.7290, -3.5200, "EX4 6LG"), # Old Tiverton Rd
        (50.7150, -3.5350, "EX2 8DP"), # Haven Banks
        (50.7320, -3.5100, "EX4 7AY")  # Polsloe
    ]
    
    #Sellers
    sellers = []
    seller_ids = users_df[users_df['role'] == 'seller']['user_id'].tolist()
    
    for user_id, (lat, lon, pcode) in zip(seller_ids, exeter_data):
        sellers.append({
            'user_id': user_id,
            'seller_name': fake.company(),
            'verified_by': random.choice(admin_ids),
            'verification_date': START_DATE - timedelta(days=15),
            'address_line1': fake.street_address(),
            'city': 'Exeter',
            'latitude': lat,
            'longitude': lon,
            'post_code': pcode,
            'country': 'United Kingdom'
        })
        
    #consumers
    consumers = []
    consumer_ids = users_df[users_df['role'] == 'consumer']['user_id'].tolist()
    for uid in consumer_ids:
        consumers.append({
            'user_id': uid,
            'fName': fake.first_name(),
            'lName': fake.last_name()
        })
        
    # admins
    admins = []
    admin_names = {
        "Muhammed": "Panjwani", "Massimo": "Belmonte", "Thomas": "Noakes",
        "Noe": "Bouchard", "Misha": "Artemiev", "Furkan": "Yalcintepe", "Ed": "Ed_lol"
    }
    for userid, (first, last) in zip(admin_ids, admin_names.items()):
        admins.append({
            'user_id': userid,
            'fName': first,
            'lName': last
        })
        
    return pd.DataFrame(sellers), pd.DataFrame(consumers), pd.DataFrame(admins)

def generate_inventory(seller_ids, categories_df, windows_df):
    """makes 2 bundles for each seller every day for the 6 weeks"""
    category_ids = categories_df['category_id'].tolist()
    window_records = windows_df.to_dict('records')
    bundles = []
    bundle_id = 1
    for day in range(WEEKS * 7):
        current_date = START_DATE + timedelta(days=day)
        for seller_id in seller_ids:
            for _ in range(2): 
                # Pick a random window (e.g., 8am-9am or 2pm-3pm)
                window = random.choice(window_records)
                
                win_start = current_date.replace(hour=window['window_start'], minute=0)
                win_end = current_date.replace(hour=window['window_end'], minute=0)
                
                bundles.append({
                    'bundle_id': bundle_id,
                    'seller_id': seller_id,
                    'bundle_name': f"Surplus {fake.word().capitalize()} Bag",
                    'description': fake.sentence(nb_words=10),
                    'total_qty': random.randint(1, 5),
                    'price': round(random.uniform(3.00, 7.50), 2),
                    'discount_percentage': random.choice([50, 60, 70]),
                    'window_start': win_start,
                    'window_end': win_end,
                    'created_at': win_start - timedelta(hours=random.randint(2, 6))
                })
                bundle_id += 1
    return pd.DataFrame(bundles)

def generate_categories():
    """Creates the master list of product categories."""
    # Using DEFAULT_CATEGORY_NAMES list
    categories = []
    for i, name in enumerate(DEFAULT_CATEGORY_NAMES, start=1):
        categories.append({
            'category_id': i,
            'category_name': name
        })
    return pd.DataFrame(categories)

def generate_bundle_categories(bundles_df, categories_df):
    """Links each bundle to 1-2 random categories."""
    bundle_ids = bundles_df['bundle_id'].tolist()
    category_ids = categories_df['category_id'].tolist()
    links = []
    
    for bundle_id in bundle_ids:
        # Most bundles belong to 1 category, some might belong to 2
        selected = random.sample(category_ids, random.randint(1, 2))
        for category_id in selected:
            links.append({
                'bundle_id': bundle_id, 
                'category_id': category_id
            })
            
    return pd.DataFrame(links)

def generate_pickup_windows():
    """creates a list of pickup time windows from 8am in 1 hour increments for the 10 windows"""
    windows = []
    start_hour = 8
    for _ in range(NUM_PICKUP_WINDOWS):
        windows.append({'window_start': start_hour, 'window_end': start_hour + 1})
        start_hour += 1
    return pd.DataFrame(windows)

def generate_reservations(bundles_df, consumers_df):
    """creates reservations with collected, no-show, and expired (reserved) states"""
    statuses = (
        ['no-show'] * NUM_NO_SHOWS
        + ['reserved'] * NUM_EXPIRIES
        + ['collected'] * (NUM_RESERVATIONS - NUM_NO_SHOWS - NUM_EXPIRIES)
    )
    random.shuffle(statuses)

    reservations = []
    claim_codes = set()
    # create a list of bundle records from the bundles dataframe
    bundle_records = bundles_df.to_dict('records')
    # create a list of consumer ids from the consumers dataframe
    consumer_ids = consumers_df['user_id'].tolist()

    for reservation_id, status in enumerate(statuses, start=1):
        bundle = random.choice(bundle_records)
        reserved_at = bundle['window_start'] - timedelta(hours=random.randint(1, 24))
        if reserved_at > bundle['window_end']:
            reserved_at = bundle['window_start']

        if status == 'collected':
            window_minutes = int((bundle['window_end'] - bundle['window_start']).total_seconds() / 60)
            collected_at = bundle['window_start'] + timedelta(
                minutes=random.randint(10, max(10, window_minutes))
            )
        else:
            collected_at = None

        while True:
            # create a unique claim code (10 uppercase characters long)
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if code not in claim_codes:
                claim_codes.add(code)
                break

        reservations.append({
            'reservation_id': reservation_id,
            'bundle_id': bundle['bundle_id'],
            'consumer_id': random.choice(consumer_ids),
            'reserved_at': reserved_at,
            'claim_code': code,
            'status': status,
            'collected_at': collected_at
        })

    return pd.DataFrame(reservations)

def generate_issue_reports(reservations_df, users_df):
    """creates seller and admin issue reports"""
    seller_issue_types = [
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
    ]
    admin_issue_types = [
        'LOGIN_FAILED',
        'ACCOUNT_LOCKED',
        'PASSWORD_RESET_FAILED',
        'PAYMENT_FAILED',
        'APP_CRASH',
        'DATA_INCONSISTENCY',
        'PERMISSION_ERROR',
        'OTHER'
    ]
    statuses = ['open', 'in_progress', 'closed']
    # split the reports into seller and admin reports (70 % seller, 30 % admin)
    seller_reports_count = int(NUM_REPORTS * 0.7)
    admin_reports_count = NUM_REPORTS - seller_reports_count

    reservation_ids = reservations_df['reservation_id'].tolist()
    user_ids = users_df['user_id'].tolist()

    seller_reports = []
    for report_id in range(1, seller_reports_count + 1):
        seller_reports.append({
            'report_id': report_id,
            'reservation_id': random.choice(reservation_ids),
            'issue_type': random.choice(seller_issue_types),
            # random realistic sentence (to be improved)
            'description': fake.sentence(nb_words=12),
            'created_at': START_DATE + timedelta(days=random.randint(0, WEEKS * 7 - 1)),
            'status': random.choice(statuses)
        })

    admin_reports = []
    for report_id in range(1, admin_reports_count + 1):
        admin_reports.append({
            'report_id': report_id,
            'user_id': random.choice(user_ids),
            'issue_type': random.choice(admin_issue_types),
            # random realistic sentence (to be improved)
            'description': fake.sentence(nb_words=12),
            'created_at': START_DATE + timedelta(days=random.randint(0, WEEKS * 7 - 1)),
            'status': random.choice(statuses)
        })

    return pd.DataFrame(seller_reports), pd.DataFrame(admin_reports)

def generate_allergens():
    allergen_names = ['Gluten', 'Dairy', 'Nuts', 'Soy', 'Eggs', 'Sesame']
    allergens = []
    for i, name in enumerate(allergen_names, start=1):
        allergens.append({'allergen_id': i, 'name': name})
    return pd.DataFrame(allergens)

def generate_bundle_allergens(bundles_df, allergens_df):
    """links each bundle to 1-3 random allergens."""
    bundle_ids = bundles_df['bundle_id'].tolist()
    allergen_ids = allergens_df['allergen_id'].tolist()
    links = []
    for bundle_id in bundle_ids:
        # pick a random number of allergens for this food bag
        selected = random.sample(allergen_ids, random.randint(0, 3))
        for allergen_id in selected:
            links.append({'bundle_id': bundle_id, 'allergen_id': allergen_id})
    return pd.DataFrame(links)

def generate_inbox(users_df):
    """generates welcome messages and system notifications."""
    user_ids = users_df['user_id'].tolist()
    messages = []
    for i in range(1, 101): # 100 sample messages
        recip = random.choice(user_ids)
        messages.append({
            'message_id': i,
            'user_id': recip,
            'sender_id': 1, # assuming user_id 1 is the system/admin can be changed easily
            'message_subject': "Welcome to the App!",
            'message_text': fake.paragraph(nb_sentences=3),
            'sent_at': START_DATE + timedelta(days=random.randint(0, 30)),
            'read_status': random.choice([True, False])
        })
    return pd.DataFrame(messages)

def generate_badges(consumers_df):
    """Creates badge definitions and assigns them to consumers."""
    #Badge Definitions
    badge_data = [
        {'badgeID': 1, 'name': 'First Save', 'description': 'Saved your first bag'},
        {'badgeID': 2, 'name': 'Eco Saver', 'description': 'Saved 10 bags total'},
        {'badgeID': 3, 'name': 'Early Bird', 'description': 'Picked up a bag before 10am'},
        {'badgeID': 4, 'name': 'Streak', 'description': 'Saved bags 3 days in a row'}
    ]
    
    #Badges Acquired (Junction)
    acquired = []
    consumer_ids = consumers_df['user_id'].tolist()
    
    for uid in consumer_ids:
        # 40% chance a user has badges
        if random.random() < 0.4:
            # Assign 1 to 3 random badges
            num_badges = random.randint(1, 3)
            my_badges = random.sample([b['badgeID'] for b in badge_data], num_badges)
            
            for bid in my_badges:
                acquired.append({
                    'user_id': uid,
                    'badge_id': bid,
                    'aquired_at': START_DATE + timedelta(days=random.randint(1, 40))
                })
                
    return pd.DataFrame(badge_data), pd.DataFrame(acquired)

def generate_tokens(users_df):
    """Generates auth tokens for the token table."""
    tokens = []
    for user_id in users_df['user_id']:
        if random.random() > 0.2: 
            created = START_DATE + timedelta(days=random.randint(1, 40))
            tokens.append({
                'token_id': len(tokens) + 1,
                'user_id': user_id,
                'token': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
                'created_at': created,
                'expires_at': created + timedelta(hours=24)
            })
    return pd.DataFrame(tokens)

# main execution
if __name__ == "__main__":
    print("Starting Data Gen...")

    # Define Output Folder
    OUTPUT_FOLDER = 'synthetic_data'
    # Create the folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created folder: {OUTPUT_FOLDER}")

    #Users & Profiles
    df_users = generate_users()
    df_sellers, df_consumers, df_admins = generate_profiles(df_users)
    print(f"   Generated {len(df_users)} users")
    
    # categories, allergens, and pickup windows
    df_categories = generate_categories()
    df_allergens = generate_allergens()
    df_windows = generate_pickup_windows()
    
    #Inventory
    df_bundles = generate_inventory(df_sellers['user_id'].tolist(), df_categories, df_windows)
    
    #Junction Tables
    df_bundle_cats = generate_bundle_categories(df_bundles, df_categories)
    df_bundle_alls = generate_bundle_allergens(df_bundles, df_allergens)
    print(f"   Generated {len(df_bundles)} bundles")
    
    # reservations with different states (collected, no-show, expired)
    df_reservations = generate_reservations(df_bundles, df_consumers)
    print(f"   Generated {len(df_reservations)} reservations")
    
    #support and game
    df_seller_reports, df_admin_reports = generate_issue_reports(df_reservations, df_users)
    df_inbox = generate_inbox(df_users)
    df_badges, df_badges_acquired = generate_badges(df_consumers)
    df_tokens = generate_tokens(df_users)

    #saving
    all_dfs = {
        'users': df_users,
        'sellers': df_sellers,
        'consumers': df_consumers,
        'admins': df_admins,
        'bundles': df_bundles,
        'categories': df_categories,
        'allergens': df_allergens,
        'bundle_category': df_bundle_cats,
        'bundle_allergens': df_bundle_alls,
        'reservations': df_reservations,
        'seller_issue_report': df_seller_reports,
        'admin_issue_report': df_admin_reports,
        'inbox': df_inbox,
        'badges': df_badges,
        'badges_acquired': df_badges_acquired,
        'token': df_tokens,
    }

    print("Saving files...")
    for name, df in all_dfs.items():
        # Use os.path.join to work on Windows and Mac
        file_path = os.path.join(OUTPUT_FOLDER, f"{name}.csv")
        df.to_csv(file_path, index=False)
        print(f"   - Saved {file_path}")

    print("Data Gen done yippee hurray")