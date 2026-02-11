import pandas as pd
import os

'''
The goal is to analyise the synthetic data and output tables of the anaysis 
which will be used in the frontend to display the data in a more user friendly way.
similar format to dataGen.py just not generating but extracting the data from the csv 
files made earlier and performing analysis for the *sellers 
* = unsure
'''

#loading data from the synthetic data csv files
bundles_df = pd.read_csv(os.path.join("synthetic_data", "bundles.csv"))
sellers_df = pd.read_csv(os.path.join("synthetic_data", "sellers.csv"))
reservations_df = pd.read_csv(os.path.join("synthetic_data", "reservations.csv"))
category_df = pd.read_csv(os.path.join("synthetic_data", "category.csv"))
bundle_category_df = pd.read_csv(os.path.join("synthetic_data", "bundle_category.csv"))