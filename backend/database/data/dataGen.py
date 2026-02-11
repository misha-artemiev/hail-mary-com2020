'''Needs checks for attributes of the tables, I will double check but a triple check would be good.
I have added some comments to the code to explain what each part is doing, but feel free to
ask if you have any questions if you need to understand.'''

'''This code generates synthetic data for the app although it is not perfect for the final app,
from my thoughts it is okay for the prototype and will be improves later, remember for CW2 we have to
make changes to almost every aspect of the app so we can make improvements and get more realistic data 
therefore more marks for CW2.'''

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
    """this function makes the seperate user role tables from the user table returned by generate_users()"""
    admin_ids = users_df[users_df['role'] == 'admin']['user_id'].tolist() #makes a list of all ids that are admins for verifcation NOT ADMIN TABLE
    
    #handling sellers
    sellers = []
    seller_ids = users_df[users_df['role'] == 'seller']['user_id'].tolist()#makes a list of all user ids that are sellers
    for unique_id in seller_ids:
        sellers.append({
            'user_id': unique_id,
            'seller_name': fake.company(),
            'verified_by': random.choice(admin_ids),
            'verification_date': START_DATE - timedelta(days=15),
            'address_line1': fake.street_address(),
            'address_line2': fake.secondary_address(),
            'city': fake.city(),
            'post_code': fake.postcode(),
            'region': fake.county(),
            'country': 'United Kingdom'
        })
        
    # handling consumers
    consumers = []
    consumer_ids = users_df[users_df['role'] == 'consumer']['user_id'].tolist()#getting consumer ids from the users df
    for unique_id in consumer_ids:
        consumers.append({
            'user_id': unique_id,
            'fName': fake.first_name(),
            'lName': fake.last_name()
        })
        
    #handling admins
    admins = []
    admin_names = {"Muhammed": "Panjwani",
                   "Massimo": "Belmonte",
                   "Thomas" : "Noakes",
                   "Noe" : "Bouchard",
                   "Misha" : "Artemiev",
                   "Furkan" : "Yalcintepe",
                   "Ed" : "Ed_lol"} 
    for unique_id, (first, last) in zip(admin_ids, admin_names.items()):
        admins.append({
            'user_id': unique_id,
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
