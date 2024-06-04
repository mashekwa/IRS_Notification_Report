import schedule
import time
from dhis2 import Api, RequestException
from services.get_org_units import pull_orgs
from services.get_irs_de import pull_irs_de
from services.get_microplan_de import  pull_microplan_de
from services.get_irs_data import pull_irs_data
from services.get_microplan_data import pull_microplan_data
from services.irs_data_process import process_data_irs
from services.data_process import run_aggregation
from dotenv import load_dotenv, dotenv_values
import os
from utils.load_to_db import load_data
import sqlite3

load_dotenv()

db_name = os.getenv("DB_NAME")
user = os.getenv("DHIS2_USER")
password = os.getenv("DHIS2_PASS")

api = Api('https://dhis.co.zm/dhis', user, password)

def initialize():
    # Pull Org Units from MRRS, Run every week in case of new orgs beeing added.
    pull_orgs(api)

    # # Pull IRS program data elements and load into DB
    pull_irs_de(api)

    # # Pull Microplan Program Data Elements
    pull_microplan_de(api)


# Check if irs_de_tbl exists before pulling data
def ensure_table_exists():
    try:
        with sqlite3.connect(f"db/{db_name}") as conn:
            cur = conn.cursor()
            res = cur.execute("SELECT name FROM sqlite_master")
            if res.fetchone() is None:
                print("Table irs_de_tbl does not exist. Running initialize() to create the table.")
                initialize()
    except sqlite3.Error as e:
        print("Something went wrong...!!!")
        print()
        print(e)  

    conn.close()

# Pull Data, Monday, Wednesday, Saturday.
def pull_microplan_irs_data():
    ensure_table_exists()
    pull_irs_data(api)
    pull_microplan_data(api)

def data_processing():
    process_data_irs()

# def generate_report():
#     pass

# def send_report():
#     pass

print("Running Initial scripts")
initialize()

# Pull Data, Monday, Wednesday, Saturday.
print("### Test")
pull_microplan_irs_data()
print("### Test 2")
process_data_irs()
print("### Test 3")
# run_aggregation()