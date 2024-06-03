import sqlite3
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()
ROOT_DIR = os.path.abspath(os.curdir)
print(ROOT_DIR)

def create_sqlite_database(filename):
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_sqlite_database()