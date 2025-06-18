import sqlite3
import logging
import os
from datetime import datetime

# Define column names for the houses table
house_columns = [
    "url_key",
    "area",
    "city",
    "price_exc",
    "price_inc",
    "available_from",
    "max_register",
    "contract_type",
    "rooms",
    "pushed"
]


def get_db_path():
    return os.path.join(os.path.dirname(__file__), "houses.db")

def get_log_path():
    return os.path.join(os.path.dirname(__file__), "house_sync.log")

# Configure logging
logging.basicConfig(
    filename=get_log_path(),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Function to create a database connection
def create_connection():
    try:
        conn = sqlite3.connect(get_db_path())
        logging.info("Database connection created")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error creating database connection: {e}")
    return None

# Function to create the houses table
def create_table():
    conn = create_connection()
    if conn is None:
        return

    try:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS houses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      url_key TEXT,
                      area TEXT,
                      city TEXT,
                      price_exc TEXT,
                      price_inc TEXT,
                      available_from TEXT,
                      max_register TEXT,
                      contract_type TEXT,
                      rooms TEXT,
                      pushed INTEGER DEFAULT 0,
                      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                      occupied_at TEXT DEFAULT NULL)"""
        )
        c.execute("""CREATE INDEX IF NOT EXISTS idx_url_key ON houses (url_key)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_occupied_at ON houses (occupied_at)""")
        conn.commit()
        logging.info("Table 'houses' created if not exists")
    except sqlite3.Error as e:
        logging.error(f"Error creating table: {e}")
    finally:
        conn.close()

# Function to sync houses and update occupied_at
def sync_houses(city_id, houses):
    conn = create_connection()
    if conn is None:
        return []

    c = conn.cursor()
    new_houses = []
    try:
        c.execute("""SELECT url_key FROM houses WHERE city = ? AND occupied_at IS NULL""", (city_id,))
        existing_houses = set(row[0] for row in c.fetchall())

        new_houses_url_keys = {house["url_key"] for house in houses}
        to_be_updated = existing_houses - new_houses_url_keys
        if to_be_updated:
            update_query = f"""UPDATE houses SET occupied_at = ? WHERE occupied_at IS NULL AND url_key IN ({','.join(['?'] * len(to_be_updated))})"""
            c.execute(update_query, (datetime.now().isoformat(),) + tuple(to_be_updated))

        to_be_inserted = []
        for house in houses:
            if house["url_key"] not in existing_houses:
                row = tuple(house[column] if column != "pushed" else 0 for column in house_columns)
                to_be_inserted.append(row)
                new_houses.append(house)

        if to_be_inserted:
            insert_query = f"""INSERT INTO houses ({','.join(house_columns)}) VALUES ({','.join(['?'] * len(house_columns))})"""
            c.executemany(insert_query, to_be_inserted)
            conn.commit()
            logging.info(f"{len(new_houses)} new houses inserted into the database")

    except sqlite3.Error as e:
        logging.error(f"Error syncing houses: {e}")
    finally:
        conn.close()

    return new_houses

# Function to mark a house as pushed
def mark_as_pushed(url_key):
    conn = create_connection()
    if conn is None:
        return
    try:
        c = conn.cursor()
        c.execute("""UPDATE houses SET pushed = 1 WHERE url_key = ?""", (url_key,))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error updating pushed status: {e}")
    finally:
        conn.close()
