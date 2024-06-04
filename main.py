import schedule
import time
from dhis2 import Api, RequestException
from services import get_org_units
from services import get_irs_de
from services import get_microplan_de
from services import get_irs_data
from services import get_microplan_data
from services import irs_data_process
from services.data_aggregator import run_aggregation
from dotenv import load_dotenv, dotenv_values
import os
from utils.load_to_db import load_data
import sqlite3
import logging

load_dotenv()

# Create and configure logger
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

db_name = os.getenv("DB_NAME")
user = os.getenv("DHIS2_USER")
password = os.getenv("DHIS2_PASS")

api = Api('https://dhis.co.zm/dhis', user, password)

def initialize():
    # Pull Org Units from MRRS, Run every week in case of new orgs beeing added.
    get_org_units.pull_orgs(api)

    # Pull IRS program data elements and load into DB
    get_irs_de.pull_irs_de(api)

    # Pull Microplan Program Data Elements
    get_microplan_de.pull_microplan_de(api)

    return schedule.CancelJob

# Create a new scheduler
scheduler = schedule.Scheduler()

# Schedule the initialize function to run once at runtime
initialize()

def pull_microplan_irs_data():
    get_irs_data.pull_irs_data(api)
    get_microplan_data.pull_microplan_data(api)

def data_processing():
    irs_data_process.process_data_irs()
    run_aggregation()


pull_microplan_irs_data()
data_processing()

# # Schedule tasks
# scheduler.every().sunday.at("01:00").do(pull_microplan_irs_data)
# scheduler.every().wednesday.at("01:00").do(pull_microplan_irs_data)
# scheduler.every().sunday.at("02:45").do(process_data_irs)
# scheduler.every().wednesday.at("02:45").do(process_data_irs)
# scheduler.every().sunday.at("04:00").do(run_aggregation)
# scheduler.every().wednesday.at("04:00").do(run_aggregation)

# def run_scheduler():
#     while True:
#         scheduler.run_pending()
#         time.sleep(1)

# # Start the scheduler
# if __name__ == "__main__":
#     run_scheduler()
