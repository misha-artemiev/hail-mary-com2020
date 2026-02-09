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