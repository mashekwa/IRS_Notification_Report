import pandas as pd
from dhis2 import Api, RequestException
import requests
from io import StringIO
import sqlite3
from dotenv import load_dotenv, dotenv_values
import os
from utils.load_to_db import load_data

load_dotenv()

def org_unit_processing(data):
    # Create a pandas DataFrame
    print("Cleaning org units....")
    df = pd.DataFrame(data)

    # drop all rows that are empty in the facility and facility_uid columns
    df = df.dropna(subset=['facility', 'facility_uid'])

    df = df[~df.apply(lambda row: row.astype(str).str.startswith(('zz Test', 'zm Test')).any(), axis=1)]

    # Add a new column 'country' and populate it with 'Zambia'
    df.insert(0, 'country', 'Zambia')

    # Sort the DataFrame by 'province', 'district', and 'facility' in ascending order
    df = df.sort_values(by=['province', 'district', 'facility'], ascending=[True, True, True])   

    # Remove province Prefix from Province and district as well as Province and District suffix
    def clean_province(value):
        # Remove the first 2 characters
        cleaned_value = value[2:]
        # Remove the word "province"
        cleaned_value = cleaned_value.replace('Province', '')
        # Strip leading and trailing whitespace
        return cleaned_value.strip()

    def clean_district(value):
        # Remove the first 2 characters
        cleaned_value = value[2:]
        # Remove the word "province"
        cleaned_value = cleaned_value.replace('District', '')
        # Strip leading and trailing whitespace
        return cleaned_value.strip()


    # Apply the function to the 'province' column
    df['province'] = df['province'].apply(clean_province)
    df['district'] = df['district'].apply(clean_district)

     # Assuming df is your DataFrame
    df.drop_duplicates(inplace=True)

    # Drop rows where facility_uid is NaN, None, or an empty string
    org_units = df.dropna(subset=['facility_uid'])
    org_units = org_units[org_units['facility_uid'].str.strip() != '']

    # Save the DataFrame to a SQL lite db
    load_data("org_units", org_units)


def pull_orgs(api):
    try:
        print("Pulling Org units from DHIS2 ....")
        response = api.get_sqlview('hsfcjU12wEM', var={'valueType': 'INTEGER'}, merge=True)
        org_unit_processing(response)

    except RequestException as e:
        print("Something went wrong..!!")
        print()
        print(e)


if __name__ == '__main__':
    pull_orgs()

