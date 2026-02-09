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