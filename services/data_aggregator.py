import pandas as pd
import sqlite3
from utils.read_from_db import read_data
from dotenv import load_dotenv, dotenv_values
import os
import logging

# Create and configure logger
logging.basicConfig(filename="system_logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

load_dotenv()

con = sqlite3.connect("db/irs.db")

def pull_data(con):
    try:
        logger.info("pulling data from Database tables")
        stage3_df = pd.read_sql_query("SELECT * from stage4_aggregate_irs_data", con)
        org_unit_df = pd.read_sql_query("SELECT * from org_units", con)
        microplan_df = pd.read_sql_query("SELECT * from microplan_data_tbl", con)
        logger.info("Data pulled successfully")
        return stage3_df, org_unit_df, microplan_df, "success"
    except Exception as e:
        logging.exception("Exception occurred: %s", str(e))
        return "fail"
    

stage3_df, org_unit_df, microplan_df,pull_status = pull_data(con)

# CLEAN ALL DATA
def clean_df(stage3_df, org_unit_df, microplan_df):
    try:
        print("Cleaning data up")
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
        print("cleaning data completed")
        return final_df, 'success'
    except Exception as e:
        logging.exception("Exception occurred: %s", str(e))
        return "fail"
    
def provincial_aggregation(final_df):
    try:
        print("Provincial picture aggregation")
        provincial = final_df.copy()
        provincial.drop(["country", "district", "facility", "facility_uid"], axis=1, inplace=True)
        provincial = provincial.groupby('province').sum()

        # Ensure numeric values for division operation
        provincial["IRS-Total Structures Sprayed"] = pd.to_numeric(provincial["IRS-Total Structures Sprayed"], errors='coerce')
        provincial["IRS-Total Structures Found"] = pd.to_numeric(provincial["IRS-Total Structures Found"], errors='coerce')

        # Calculate % population protected
        provincial["pop_protected_perc"] = round((provincial["IRS-Total Population Protected"] / provincial["IRS-Total Targeted Population"].fillna(0)) * 100)
        provincial.loc[provincial['IRS-Total Targeted Population'] == 0, 'pop_protected_perc'] = 0

        # Calculate Spray progress
        provincial["spray_progress"] = round((provincial["IRS-Total Structures Sprayed"] / provincial["IRS-Total Targeted Eligible Structures"].fillna(0)) * 100)
        provincial.loc[provincial['IRS-Total Targeted Eligible Structures'] == 0, 'spray_progress'] = 0

        # Calculate spray coverage
        provincial["spray_coverage"] = round((provincial["IRS-Total Structures Sprayed"] / provincial["IRS-Total Structures Found"]) * 100)

        print("Provincial picture aggregation, COMPLETE")
        print("Loading Provincial picture aggregation to DB")
        con = sqlite3.connect("db/irs.db")
        provincial.to_sql("provincial_progress", con, if_exists="replace")
        print("Loading Provincial picture aggregation to DB...., COMPLETE")

        return provincial
    except Exception as e:
        logging.exception("Exception occurred: %s", str(e))
        return "fail"
    

def district_aggregation(final_df):
    try:
        print("District picture aggregation")
        district = final_df.copy()
        district.drop(["country", "facility", "facility_uid"], axis=1, inplace=True)

        district = district.groupby(['province', 'district'], as_index=False).sum()

        # Ensure numeric values for division operation
        district["IRS-Total Structures Sprayed"] = pd.to_numeric(district["IRS-Total Structures Sprayed"], errors='coerce')
        district["IRS-Total Structures Found"] = pd.to_numeric(district["IRS-Total Structures Found"], errors='coerce')

        # Calculate % population protected.
        district["pop_protected_perc"] = round((district["IRS-Total Population Protected"] / district["IRS-Total Targeted Population"].fillna(0)) * 100)
        district.loc[district['IRS-Total Targeted Population'] == 0, 'pop_protected_perc'] = 0

        # Calculate Spray progress
        district["spray_progress"] = round((district["IRS-Total Structures Sprayed"] / district["IRS-Total Targeted Eligible Structures"].fillna(0)) * 100)
        district.loc[district['IRS-Total Targeted Eligible Structures'] == 0, 'spray_progress'] = 0

        # Calculate spray coverage
        district["spray_coverage"] = round((district["IRS-Total Structures Sprayed"] / district["IRS-Total Structures Found"]) * 100)

        print("District picture aggregation, COMPLETE")
        print("Loading District picture aggregation to DB")
        con = sqlite3.connect("db/irs.db")
        district.to_sql("district_progress", con, if_exists="replace")
        print("Loading District picture aggregation to DB...., COMPLETE")
        return district
    except Exception as e:
        logging.exception("Exception occurred: %s", str(e))
        print(e)
        return "fail"


def process_plus(stage3_df, org_unit_df, microplan_df , pull_status):
    if pull_status == 'success':
        try:
            final_df, clean_status = clean_df(stage3_df, org_unit_df, microplan_df)
            return final_df, "success"
        except Exception as e:
            return "fail"
        

def run_aggregation():
    stage3_df, org_unit_df, microplan_df , pull_status= pull_data(con)
#     print(pull_status)
#     print(len(stage3_df))
#     print(len(org_unit_df))
#     print(len(microplan_df))
    final_df, process_status = process_plus(stage3_df, org_unit_df, microplan_df , pull_status)

    if process_status == 'success':
        provincial_aggregation(final_df)
        district_aggregation(final_df)
        return 'success'
    else:
        return 'fail'
    

if __name__ == '__main__':
    run_aggregation()

