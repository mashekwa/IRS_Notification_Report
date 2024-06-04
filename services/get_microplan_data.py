import pandas as pd
from dhis2 import Api
import requests
from io import StringIO
from utils.read_from_db import read_data
from utils.load_to_db import load_data
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

# start_date = os.getenv("CAMPAIGN_START_DATE")
start_date = '2023-09-01'
end_date = os.getenv("CAMPAIGN_END_DATE")
ou = os.getenv("COUNTRY_ID") # Country Org Unit ID from DHIS2
program = os.getenv("IRS_MICROPLAN_PROGRAM_ID")

params={
    'orgUnit':ou,
    'ouMode':'DESCENDANTS',
    'program':program, 
    'startDate':start_date,
    'endDate':end_date,
    'fields':'storedBy,event,eventDate,created,lastUpdated,programStage,orgUnit,deleted,dataValues[dataElement,value]'
    }

def get_microplan_data(api):
    print("Pulling data from DHIS2")
    all_pages = api.get_paged('events', params=params, page_size=1000, merge=True)
    events = all_pages['events']
    print(f'{len(events)} records retrieved from Server')

    return events


def events_to_df(events, elements_df):
    # Creating a DataFrame
    microplan_df = pd.json_normalize(events, 'dataValues', ['event','eventDate','created','lastUpdated','programStage','orgUnit','deleted'])

    #change date types
    microplan_df['eventDate'] = pd.to_datetime(microplan_df['eventDate'])
    microplan_df['created'] = pd.to_datetime(microplan_df['created'])
    microplan_df['lastUpdated'] = pd.to_datetime(microplan_df['lastUpdated'])


    # Pivot the DataFrame
    pivot_df = microplan_df.pivot_table(index=['event','eventDate','created','lastUpdated','programStage','orgUnit','deleted'],
                            columns='dataElement', values='value', aggfunc='first')

    # Reset the index
    pivot_df.reset_index(inplace=True)

    # Create a dictionary mapping ids to names
    id_to_name = dict(zip(elements_df['id'], elements_df['name']))

    # Rename columns of events_df using the dictionary
    pivot_df.rename(columns=id_to_name, inplace=True)

    #Delete deleted rows
    pivot_df = pivot_df[pivot_df['deleted'] != True]
    pivot_df.drop(["programStage","deleted"], axis = 1, inplace=True)

    #change date types
    pivot_df['IRS- Campaign Start Date'] = pd.to_datetime(pivot_df['IRS- Campaign Start Date'])
    pivot_df['IRS- Campaign End Date'] = pd.to_datetime(pivot_df['IRS- Campaign End Date'])
    pivot_df['IRS-Total Eligible  Structures'] = pd.to_numeric(pivot_df['IRS-Total Eligible  Structures'], errors='coerce')
    pivot_df['IRS-Total Targeted Eligible Structures'] = pd.to_numeric(pivot_df['IRS-Total Targeted Eligible Structures'], errors='coerce')
    pivot_df['IRS-Total Targeted Population'] = pd.to_numeric(pivot_df['IRS-Total Targeted Population'], errors='coerce')
    pivot_df['IRS-Total Population'] = pd.to_numeric(pivot_df['IRS-Total Population'], errors='coerce')

    # Sort Date on event created date
    df_sorted = pivot_df.sort_values(by='created', ascending=False)

    # Drop duplicates based on specified columns, keeping the first occurrence (newest record)
    # df_no_duplicates = df_sorted.drop_duplicates(subset=['eventDate', 'orgUnit', 'IRS- Campaign Start Date','IRS- Campaign End Date'])

    # Group by 'orgUnit' and get the index of the row with the most recent 'lastUpdated'
    idx = df_sorted.groupby('orgUnit')['lastUpdated'].idxmax()

    # Use the indexes to create a new DataFrame with the most recent rows
    final_df = df_sorted.loc[idx]
    final_df.drop(["event","eventDate","created","lastUpdated"], axis = 1, inplace=True)

    return final_df

def pull_microplan_data(api):
    # Load data Elements from data file
    microplan_de_tbl = 'microplan_de_tbl'
    elements_df = read_data(microplan_de_tbl)

    events = get_microplan_data(api)

    if len(events) != 0:
        df = events_to_df(events, elements_df)

        if df.empty:
            print("IRS Microplan data pull returned empty values")
        else:
            load_data("microplan_data_tbl", df)


if __name__ == '__main__':
    pull_microplan_data()






