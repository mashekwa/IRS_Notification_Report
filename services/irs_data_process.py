import pandas as pd
import requests
from io import StringIO
import sqlite3
from utils.load_to_db import load_data

def irs_data_cleanup(stage1_df, con):
    # Define the columns to convert to numeric
    columns_to_convert = [
        'IRS-Reason Rooms Not Sprayed: Refused',
        'IRS-Insecticide Units Used',
        'IRS-Pregnant Women Sleeping Under Nets',
        'IRS-Total Nets Available',
        'IRS-Children <5 Yrs Sleeping Under Nets',
        'IRS-Females Protected',
        'IRS-Total People Sleeping Under Nets',
        'IRS-Eligible Rooms Sprayed',
        'IRS-No of Spray Operators',
        'IRS-Reason Structures Not Sprayed: Other',
        'IRS-Insecticides Units Returned Full',
        'IRS-Reason Rooms Not Sprayed: Sick',
        'IRS-Reason Structures Not Sprayed: Locked',
        'IRS-Reason Rooms Not Sprayed: No Insecticide',
        'IRS-Total Nets Being Used',
        'IRS-Reason Rooms Not Sprayed: Other',
        'IRS-Total People Protected',
        'IRS-Total Population Found',
        'IRS-No of Supervisors',
        'IRS-Reason Structures Not Sprayed: Not Home',
        'IRS-Insecticides Units Returned Empty',
        'IRS-Males Protected',
        'IRS-Reason Rooms Not Sprayed: Other'
    ]

    # Convert columns to numeric if they exist in the DataFrame
    for column in columns_to_convert:
        if column in stage1_df.columns:
            stage1_df[column] = pd.to_numeric(stage1_df[column], errors='coerce')

    # Drop duplicates based on specific columns if they exist
    subset_columns = ['orgUnit', 'dataElement', 'categoryOptionCombo']
    existing_subset_columns = [col for col in subset_columns if col in stage1_df.columns]
    if existing_subset_columns:
        stage1_df.drop_duplicates(subset=existing_subset_columns, inplace=True)

    # Create index
    stage1_df.reset_index(drop=True, inplace=True)
    
    # Drop extra index column if exists
    if 'level_0' in stage1_df.columns:
        stage1_df.drop(columns=['level_0'], inplace=True)
    
    load_data("stage1_irs_data", stage1_df)

def irs_data_aggregate(df, con):
    df_no_duplicates = df.copy()  # Ensure df_no_duplicates is a copy, not a view

    columns_to_convert = [
        'IRS-Reason Rooms Not Sprayed: Other',
        'IRS-Total Nets Being Used',
        'IRS-Reason Structures Not Sprayed: Not Home/Missed',
        'IRS-Total Population Protected',
        'IRS-Pregnant Women Protected',
        'IRS-Insecticide Units Received',
        'IRS-Total Structures Sprayed',
        'IRS-Males Protected',
        'IRS-Reason Rooms Not Sprayed: Locked',
        'IRS-Insecticide Units Missing',
        'IRS-Eligible Rooms Found'
    ]

    for column in columns_to_convert:
        if column in df_no_duplicates.columns:
            # Fill non-finite values with 0 before converting to int
            df_no_duplicates[column] = df_no_duplicates[column].fillna(0).astype(int)

    sum_df = df_no_duplicates.groupby('orgUnit').sum().reset_index()

    # Check if 'level_0' exists and remove it
    if 'level_0' in sum_df.columns:
        sum_df.drop(columns=['level_0'], inplace=True)

    load_data("stage4_aggregate_irs_data", sum_df)

def process_data_irs():
    con = sqlite3.connect("db/irs.db")
    
    # Load the data into a DataFrame
    stage1_df = pd.read_sql_query("SELECT * from irs_raw_data", con)
    irs_data_cleanup(stage1_df, con)

    # Load the data into a DataFrame
    stage2_df = pd.read_sql_query("SELECT * from stage1_irs_data", con)
    irs_data_aggregate(stage2_df, con)

if __name__ == '__main__':
    process_data_irs()
