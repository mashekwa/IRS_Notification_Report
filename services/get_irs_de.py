import pandas as pd
from dhis2 import Api
from dotenv import load_dotenv, dotenv_values
import os
from utils.load_to_db import load_data

load_dotenv()

db_name = os.getenv("DB_NAME")

# user = os.getenv("DHIS2_USER")
# password = os.getenv("DHIS2_PASS")
# api = Api('https://dhis.co.zm/dhis', user, password)

program = os.getenv("IRS_DATA_PROGRAM_ID")



def pull_irs_de(api):

    print(f"Pulling data elements from IRS Data program ({program})")
    # Get program stages from Program
    params={'fields':'name,id,programStages[id]'}

    stage_res = api.get(f'programs/{program}', params=params)
    data = stage_res.json()
    program_stage_id = data['programStages'][0]['id']
    # print("Program Stage ID:", program_stage_id)

    # get Data elements on program stage:
    params= {'fields':'name,id,programStageDataElements[dataElement[id,name]]'}
    elements_res = stage = api.get(f'programStages/{program_stage_id}', params=params)
    elements = elements_res.json()
    # print(elements['programStageDataElements'])

    # Extracting 'dataElement' from each dictionary in the list
    elements_data = elements['programStageDataElements']
    elements_data = [entry['dataElement'] for entry in elements_data]

    # Creating a DataFrame
    df = pd.DataFrame(elements_data, columns=['name', 'id'])

    # Load DEs to table
    load_data("irs_de_tbl", df)


if __name__ == '__main__':
    pull_irs_de()