import pandas as pd
from dhis2 import Api
from utils.read_from_db import read_data
from utils.load_to_db import load_data
from dotenv import load_dotenv
import os

load_dotenv()

start_date = os.getenv("CAMPAIGN_START_DATE")
end_date = os.getenv("CAMPAIGN_END_DATE")
ou = os.getenv("COUNTRY_ID")  # Country Org Unit ID from DHIS2
program = os.getenv("IRS_DATA_PROGRAM_ID")

params = {
    'orgUnit': ou,
    'ouMode': 'DESCENDANTS',
    'program': program,
    'startDate': start_date,
    'endDate': end_date,
    'fields': 'storedBy,event,eventDate,created,lastUpdated,programStage,orgUnit,deleted,dataValues[dataElement,value]'
}

# Load data Elements from DB
irs_de_tbl = 'irs_de_tbl'
elements_df = read_data(irs_de_tbl)

def get_irs_data(api):
    try:
        print("Pulling data from DHIS2")
        all_pages = api.get_paged('events', params=params, page_size=1000, merge=True)
        events = all_pages['events']
        print(f'{len(events)} records retrieved from Server')
        return events, "success"
    except Exception as e:
        print(f"Error occurred while pulling data: {str(e)}")
        return [], "fail"
    
def events_to_df(events):
    # Your existing code
    events_df = pd.json_normalize(events, 'dataValues', ['event','eventDate','created','lastUpdated','programStage','orgUnit','deleted'])

     # Change date types
    events_df['eventDate'] = pd.to_datetime(events_df['eventDate'])
    events_df['created'] = pd.to_datetime(events_df['created'])
    events_df['lastUpdated'] = pd.to_datetime(events_df['lastUpdated'])

    # Pivot the DataFrame
    pivot_df = events_df.pivot_table(index=['event','eventDate','created','lastUpdated','programStage','orgUnit','deleted'],
                                     columns='dataElement', values='value', aggfunc='first')

    # Reset the index
    pivot_df.reset_index(inplace=True)

    # Create a dictionary mapping ids to names
    id_to_name = dict(zip(elements_df['id'], elements_df['name']))

    # Rename columns of events_df using the dictionary
    pivot_df.rename(columns=id_to_name, inplace=True)

    # Delete deleted rows
    pivot_df = pivot_df[pivot_df['deleted'] != True]

    pivot_df.reset_index(inplace=True)

    # Check if 'level_0' exists and remove it
    if 'level_0' in pivot_df.columns:
        pivot_df.drop(columns=['level_0'], inplace=True)

    return pivot_df


def pull_irs_data(api):
    events, status = get_irs_data(api)

    if status == "success":
        if len(events) != 0:
            try:
                df = events_to_df(events)
                if df.empty:
                    print("IRS data pull returned empty values")
                else:
                    df['eventDate'] = pd.to_datetime(df['eventDate'])
                    df.sort_values(by='eventDate', inplace=True)
                    load_data("irs_raw_data", df)
            except Exception as e:
                print(f"Error occurred while processing data: {str(e)}")
                return "fail"
        else:
            print("No events retrieved from DHIS2")
            return "fail"
    else:
        return "fail"

if __name__ == '__main__':
    result = pull_irs_data()  # Pass the API object here
    if result == "success":
        print("Data pull and processing successful")
    else:
        print("Data pull and processing failed")
