import pandas as pd
import requests
from io import StringIO
import sqlite3
from utils.load_to_db import load_data

# Load data Elements from data file
def irs_data_cleanup(stage1_df):
    #change other data types
    stage1_df['IRS-Reason Rooms Not Sprayed: Refused'] = pd.to_numeric(stage1_df['IRS-Reason Rooms Not Sprayed: Refused'], errors='coerce')
    stage1_df['IRS-Insecticide Units Used'] = pd.to_numeric(stage1_df['IRS-Insecticide Units Used'], errors='coerce')
    stage1_df['IRS-Pregnant Women Sleeping Under Nets'] = pd.to_numeric(stage1_df['IRS-Pregnant Women Sleeping Under Nets'], errors='coerce')
    stage1_df['IRS-Total Nets Available'] = pd.to_numeric(stage1_df['IRS-Total Nets Available'], errors='coerce')
    stage1_df['IRS-Children <5 Yrs Sleeping Under Nets'] = pd.to_numeric(stage1_df['IRS-Children <5 Yrs Sleeping Under Nets'], errors='coerce')
    stage1_df['IRS-Females Protected'] = pd.to_numeric(stage1_df['IRS-Females Protected'], errors='coerce')
    stage1_df['IRS-Total People Sleeping Under Nets'] = pd.to_numeric(stage1_df['IRS-Total People Sleeping Under Nets'], errors='coerce')
    stage1_df['IRS-Eligible Rooms Sprayed'] = pd.to_numeric(stage1_df['IRS-Eligible Rooms Sprayed'], errors='coerce')
    stage1_df['IRS-No of Spray Operators'] = pd.to_numeric(stage1_df['IRS-No of Spray Operators'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Other'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Other'], errors='coerce')
    stage1_df['IRS-Insecticides Units Returned Full'] = pd.to_numeric(stage1_df['IRS-Insecticides Units Returned Full'], errors='coerce')
    stage1_df['IRS-Reason Rooms Not Sprayed: Sick'] = pd.to_numeric(stage1_df['IRS-Reason Rooms Not Sprayed: Sick'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Locked'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Locked'], errors='coerce')
    stage1_df['IRS-Children <5 years Protected'] = pd.to_numeric(stage1_df['IRS-Children <5 years Protected'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Funeral'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Funeral'], errors='coerce')
    stage1_df['IRS-Total Structures Not Sprayed'] = pd.to_numeric(stage1_df['IRS-Total Structures Not Sprayed'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Refused'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Refused'], errors='coerce') 
    stage1_df['IRS-Total Structures Found'] = pd.to_numeric(stage1_df['IRS-Total Structures Found'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Sick'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Sick'], errors='coerce')
    stage1_df['IRS-Total Rooms Not Sprayed'] = pd.to_numeric(stage1_df['IRS-Total Rooms Not Sprayed'], errors='coerce')
    stage1_df['IRS-Reason Rooms Not Sprayed: Other'] = pd.to_numeric(stage1_df['IRS-Reason Rooms Not Sprayed: Other'], errors='coerce')
    stage1_df['IRS-Total Nets Being Used'] = pd.to_numeric(stage1_df['IRS-Total Nets Being Used'], errors='coerce')
    stage1_df['IRS-Reason Structures Not Sprayed: Not Home/Missed'] = pd.to_numeric(stage1_df['IRS-Reason Structures Not Sprayed: Not Home/Missed'], errors='coerce') 
    stage1_df['IRS-Total Population Protected'] = pd.to_numeric(stage1_df['IRS-Total Population Protected'], errors='coerce')
    stage1_df['IRS-Pregnant Women Protected'] = pd.to_numeric(stage1_df['IRS-Pregnant Women Protected'], errors='coerce')
    stage1_df['IRS-Insecticide Units Received'] = pd.to_numeric(stage1_df['IRS-Insecticide Units Received'], errors='coerce')
    stage1_df['IRS-Total Structures Sprayed'] = pd.to_numeric(stage1_df['IRS-Total Structures Sprayed'], errors='coerce') 
    stage1_df['IRS-Males Protected'] = pd.to_numeric(stage1_df['IRS-Males Protected'], errors='coerce')
    stage1_df['IRS-Reason Rooms Not Sprayed: Locked'] = pd.to_numeric(stage1_df['IRS-Reason Rooms Not Sprayed: Locked'], errors='coerce')
    stage1_df['IRS-Insecticide Units Missing'] = pd.to_numeric(stage1_df['IRS-Insecticide Units Missing'], errors='coerce')
    stage1_df['IRS-Eligible Rooms Found'] = pd.to_numeric(stage1_df['IRS-Eligible Rooms Found'], errors='coerce')


    # Drop duplicates based on specified columns, keeping the first occurrence (newest record)
    df_no_duplicates = stage1_df.drop_duplicates(subset=['eventDate', 'orgUnit', 'IRS-Team Number','IRS-Insecticide'])

    # Check if 'level_0' exists and remove it
    if 'level_0' in df_no_duplicates.columns:
        df_no_duplicates.drop(columns=['level_0'], inplace=True)
    
    load_data("stage1_irs_data", df_no_duplicates)


def irs_data_aggregate(df):
    df_no_duplicates = df.copy()

    columns=['event',
            'eventDate',
            'created', 
            'lastUpdated', 
            'programStage', 
            'deleted',
            'IRS-Bottles or Sachets',
            'IRS-Main Spray or Mop Up',
            'IRS-Team Number',
            'IRS-Insecticide'
    ]
    df_no_duplicates.drop(columns=columns, inplace=True)

    # Fill al NaN with 0
    df_no_duplicates.fillna(0, inplace=True)

    # Covert to Interger
    df_no_duplicates['IRS-Reason Rooms Not Sprayed: Refused'] = df_no_duplicates['IRS-Reason Rooms Not Sprayed: Refused'].astype(int)
    df_no_duplicates['IRS-Insecticide Units Used'] = df_no_duplicates['IRS-Insecticide Units Used'].astype(int)
    df_no_duplicates['IRS-Pregnant Women Sleeping Under Nets'] = df_no_duplicates['IRS-Pregnant Women Sleeping Under Nets'].astype(int)
    df_no_duplicates['IRS-Total Nets Available'] = df_no_duplicates['IRS-Total Nets Available'].astype(int)
    df_no_duplicates['IRS-Children <5 Yrs Sleeping Under Nets'] = df_no_duplicates['IRS-Children <5 Yrs Sleeping Under Nets'].astype(int)
    df_no_duplicates['IRS-Females Protected'] = df_no_duplicates['IRS-Females Protected'].astype(int)
    df_no_duplicates['IRS-Total People Sleeping Under Nets'] = df_no_duplicates['IRS-Total People Sleeping Under Nets'].astype(int)
    df_no_duplicates['IRS-Eligible Rooms Sprayed'] = df_no_duplicates['IRS-Eligible Rooms Sprayed'].astype(int)
    df_no_duplicates['IRS-No of Spray Operators'] = df_no_duplicates['IRS-No of Spray Operators'].astype(int)
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Other'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Other'].astype(int)
    df_no_duplicates['IRS-Insecticides Units Returned Full'] = df_no_duplicates['IRS-Insecticides Units Returned Full'].astype(int) 
    df_no_duplicates['IRS-Reason Rooms Not Sprayed: Sick'] = df_no_duplicates['IRS-Reason Rooms Not Sprayed: Sick'].astype(int)
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Locked'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Locked'].astype(int)
    df_no_duplicates['IRS-Children <5 years Protected'] = df_no_duplicates['IRS-Children <5 years Protected'].astype(int)
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Funeral'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Funeral'].astype(int) 
    df_no_duplicates['IRS-Total Structures Not Sprayed'] = df_no_duplicates['IRS-Total Structures Not Sprayed'].astype(int)
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Refused'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Refused'].astype(int) 
    df_no_duplicates['IRS-Total Structures Found'] = df_no_duplicates['IRS-Total Structures Found'].astype(int) 
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Sick'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Sick'].astype(int) 
    df_no_duplicates['IRS-Total Rooms Not Sprayed'] = df_no_duplicates['IRS-Total Rooms Not Sprayed'].astype(int)
    df_no_duplicates['IRS-Reason Rooms Not Sprayed: Other'] = df_no_duplicates['IRS-Reason Rooms Not Sprayed: Other'].astype(int)
    df_no_duplicates['IRS-Total Nets Being Used'] = df_no_duplicates['IRS-Total Nets Being Used'].astype(int)
    df_no_duplicates['IRS-Reason Structures Not Sprayed: Not Home/Missed'] = df_no_duplicates['IRS-Reason Structures Not Sprayed: Not Home/Missed'].astype(int) 
    df_no_duplicates['IRS-Total Population Protected'] = df_no_duplicates['IRS-Total Population Protected'].astype(int) 
    df_no_duplicates['IRS-Pregnant Women Protected'] = df_no_duplicates['IRS-Pregnant Women Protected'].astype(int) 
    df_no_duplicates['IRS-Insecticide Units Received'] = df_no_duplicates['IRS-Insecticide Units Received'].astype(int) 
    df_no_duplicates['IRS-Total Structures Sprayed'] = df_no_duplicates['IRS-Total Structures Sprayed'].astype(int) 
    df_no_duplicates['IRS-Males Protected'] = df_no_duplicates['IRS-Males Protected'].astype(int) 
    df_no_duplicates['IRS-Reason Rooms Not Sprayed: Locked'] = df_no_duplicates['IRS-Reason Rooms Not Sprayed: Locked'].astype(int) 
    df_no_duplicates['IRS-Insecticide Units Missing'] = df_no_duplicates['IRS-Insecticide Units Missing'].astype(int) 
    df_no_duplicates['IRS-Eligible Rooms Found'] = df_no_duplicates['IRS-Eligible Rooms Found'].astype(int)

    sum_df = df_no_duplicates.groupby('orgUnit').sum().reset_index()
    # sum_df = sum_df.loc[:, ~sum_df.columns.duplicated()]  # Drop duplicate columns

    # Check if 'level_0' exists and remove it
    if 'level_0' in sum_df.columns:
        sum_df.drop(columns=['level_0'], inplace=True)

    # Check if 'level_0' exists and remove it
    # if 'index' in sum_df.columns:
    #     sum_df.drop(columns=['index'], inplace=True)
        
    load_data("stage4_aggregate_irs_data", sum_df)






def process_data_irs():
    con = sqlite3.connect("db/irs.db")
    # Load the data into a DataFrame
    stage1_df = pd.read_sql_query("SELECT * from irs_raw_data", con)
    irs_data_cleanup(stage1_df)


    # Load the data into a DataFrame
    stage2_df = pd.read_sql_query("SELECT * from stage1_irs_data", con)
    irs_data_aggregate(stage2_df)

if __name__ == '__main__':
    process_data_irs()
