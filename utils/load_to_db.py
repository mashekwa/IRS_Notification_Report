import pandas as pd
import sqlite3
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

db_name = os.getenv("DB_NAME")

def load_data(tbl_name, df):
    try:
        with sqlite3.connect(f"db/{db_name}") as conn:
            df.to_sql(tbl_name, conn, if_exists="replace")
            print(f"Data loaded to {tbl_name} in DB")
    except sqlite3.Error as e:
        print("Something went wrong...!!!")
        print()
        print(e)

if __name__ == '__main__':
    load_data()


