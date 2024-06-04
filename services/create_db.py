import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
ROOT_DIR = os.path.abspath(os.curdir)
print(ROOT_DIR)

def create_sqlite_database(filename):
    """Create a database connection to an SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.sqlite_version)

        # Create table org_units
        create_org_units_table = """
        CREATE TABLE IF NOT EXISTS org_units (
            country TEXT,
            province TEXT,
            district TEXT,
            facility TEXT,
            facility_uid TEXT
        );
        """
        conn.execute(create_org_units_table)

        # Create table microplan_de_tbl
        create_microplan_de_table = """
        CREATE TABLE IF NOT EXISTS microplan_de_tbl (
            name TEXT,
            de_id TEXT
        );
        """
        conn.execute(create_microplan_de_table)

        # Create table irs_de_tbl
        create_irs_de_table = """
        CREATE TABLE IF NOT EXISTS irs_de_tbl (
            name TEXT,
            de_id TEXT
        );
        """
        conn.execute(create_irs_de_table)

        conn.commit()
        print("Tables created successfully.")

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    db_file = os.path.join(ROOT_DIR, "database.db")
    create_sqlite_database(db_file)
