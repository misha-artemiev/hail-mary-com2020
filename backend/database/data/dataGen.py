'''Needs checks for attributes of the tables, I will double check but a triple check would be good.
I have added some comments to the code to explain what each part is doing, but feel free to
ask if you have any questions if you need to understand.'''

import pandas as pd
import numpy as np
import random
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
WEEKS = 6
#random start date can be changed
START_DATE = datetime(2024, 1, 1)

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
            'f_name': fake.first_name(),
            'l_name': fake.last_name()
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
            'f_name': first,
            'l_name': last
        })
        
    return pd.DataFrame(sellers), pd.DataFrame(consumers), pd.DataFrame(admins)

def generate_inventory(seller_ids):
    """makes 2 bundles for each seller every day for the 6 weeks"""
    bundles = []
    bundle_id = 1
    for day in range(WEEKS * 7):
        current_date = START_DATE + timedelta(days=day)
        for seller_id in seller_ids:
            for _ in range(2): # 2 Daily
                bundles.append({
                    'bundle_id': bundle_id,
                    'seller_id': seller_id,
                    'bundle_name': ("Surplus ", fake.word().capitalize()," Bag"),
                    'description': fake.sentence(nb_words=10),
                    'total_qty': random.randint(1, 5),
                    'price': round(random.uniform(3.00, 7.50), 2),
                    'discount_percentage': random.choice([50, 60, 70]),
                    'window_start': current_date.replace(hour=17, minute=0),
                    'window_end': current_date.replace(hour=19, minute=0),
                    'created_at': current_date.replace(hour=17, minute=0) - timedelta(hours=4)
                })
                bundle_id += 1
    return pd.DataFrame(bundles)