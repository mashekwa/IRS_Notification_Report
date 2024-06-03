import pandas as pd
import sqlite3
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

db_name = os.getenv("DB_NAME")

def read_data(tbl_name):
    try:
        with sqlite3.connect(f"db/{db_name}") as conn:
            print(f"Reading data from {tbl_name} in DB")
            df = pd.read_sql_query(f"SELECT * from {tbl_name}", conn)
    except sqlite3.Error as e:
        print("Something went wrong...!!!")
        print()
        print(e)    
    
    return df


if __name__ == '__main__':
    read_data()


