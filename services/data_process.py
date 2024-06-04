import pandas as pd
import sqlite3
from utils.read_from_db import read_data
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

con = sqlite3.connect("db/irs.db")
# Load the data into a DataFrame
def pull_data(con):
    try:
        stage3_df = pd.read_sql_query("SELECT * from stage4_aggregate_irs_data", con)
        org_unit_df = pd.read_sql_query("SELECT * from org_units", con)
        microplan_df = pd.read_sql_query("SELECT * from microplan", con)
        return stage3_df, org_unit_df, microplan_df, "success"
    except Exception as e:
        return "fail"



# CLEAN ALL DATA
def clean_df(stage3_df, org_unit_df, microplan_df):
    stage3_df.reset_index(drop=True)
    irs_data =stage3_df[['orgUnit', 'IRS-Total Population Protected','IRS-Total Structures Found','IRS-Total Structures Not Sprayed','IRS-Total Structures Sprayed']].copy()
    # AGGREGATE IRS DATA BY FACILITY
    irs_aggregate_df = irs_data.groupby('orgUnit', as_index =False).sum()

    # CLEAN MICROPLAN DATA
    microplan_df.drop(["IRS- Campaign End Date","IRS- Campaign Start Date"], axis = 1, inplace=True)
    microplan_df.reset_index(drop=True)

    merged_df = pd.merge(irs_aggregate_df, microplan_df, on="orgUnit", how="left")
    merged_df.rename(columns = {'orgUnit':'facility_uid'}, inplace = True)

    final_df = pd.merge(org_unit_df, merged_df, on="facility_uid", how="left").reset_index(drop=True)
    final_df.dropna(subset=['IRS-Total Population Protected','IRS-Total Structures Found','IRS-Total Structures Not Sprayed', 'IRS-Total Structures Sprayed'],inplace=True)
    final_df.drop(["index_x"], axis = 1, inplace=True)
    final_df.drop(["index_y"], axis = 1, inplace=True)

    return final_df



# PROVINCIAL PICTURE:
def provincial_aggregation(final_df):
    provincial = final_df.copy()
    provincial.drop(["country", "district","facility","facility_uid"], axis = 1, inplace=True)
    provincial=provincial.groupby('province').sum()
    # provincial.drop(["index_x"], axis = 1, inplace=True)

    # Calculate % population protected.
    provincial["pop_protected_perc"] = round(( provincial["IRS-Total Population Protected"] / provincial["IRS-Total Targeted Population"].fillna(0)) * 100)
    provincial.loc[provincial['IRS-Total Targeted Population'] == 0, 'pop_protected_perc'] = 0

    # Calculate Spray progress
    provincial["spray_progress"] = round(( provincial["IRS-Total Structures Sprayed"] / provincial["IRS-Total Targeted Eligible Structures"].fillna(0)) * 100)
    # Ensure that spray coverage is 0 if the denominator is 0
    provincial.loc[provincial['IRS-Total Targeted Eligible Structures'] == 0, 'spray_progress'] = 0
    provincial["spray_coverage"] = round(( provincial["IRS-Total Structures Sprayed"] / provincial["IRS-Total Structures Found"]) * 100)

    con = sqlite3.connect("db/irs.db")
    provincial.to_sql("provincial_progress", con, if_exists="replace")

    return provincial


# DISTRICT PICTURE:
def district_aggregation(final_df):
    district = final_df.copy()
    district.drop(["country", "facility","facility_uid"], axis = 1, inplace=True)

    district = district.groupby(['province', 'district'], as_index=False).sum()

    # Calculate % population protected.
    district["pop_protected_perc"] = round(( district["IRS-Total Population Protected"] / district["IRS-Total Targeted Population"].fillna(0)) * 100)
    district.loc[district['IRS-Total Targeted Population'] == 0, 'pop_protected_perc'] = 0

    # provincial.drop(["index_x"], axis = 1, inplace=True)
    district["spray_progress"] = round(( district["IRS-Total Structures Sprayed"] / district["IRS-Total Targeted Eligible Structures"].fillna(0)) * 100)
    # Ensure that spray coverage is 0 if the denominator is 0
    district.loc[district['IRS-Total Targeted Eligible Structures'] == 0, 'spray_progress'] = 0

    district["spray_coverage"] = round(( district["IRS-Total Structures Sprayed"] / district["IRS-Total Structures Found"]) * 100)

    con = sqlite3.connect("db/irs.db")
    district.to_sql("district_progress", con, if_exists="replace")

    return district



def process_plus(stage3_df, org_unit_df, microplan_df , pull_status):
    if pull_status == 'success':
        try:
            final_df = clean_df(stage3_df, org_unit_df, microplan_df)
            return final_df, "success"
        except Exception as e:
            return "fail"
        




def run_aggregation():
    stage3_df, org_unit_df, microplan_df , pull_status= pull_data(con)
    print(pull_status)
    print(len(stage3_df))
    print(len(org_unit_df))
    print(len(microplan_df))
    final_df, process_status = process_plus(stage3_df, org_unit_df, microplan_df , pull_status)

    if process_status == 'success':
        provincial_aggregation(final_df)
        district_aggregation(final_df)
        return 'success'
    else:
        return 'fail'

if __name__ == '__main__':
    result = run_aggregation()  # Pass the API object here
    






