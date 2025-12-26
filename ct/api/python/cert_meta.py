import argparse
import logging
from sql import crtmgr_database



logging.basicConfig(format="[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s", datefmt="%m/%d/%Y_%I:%M:%S")
logging.root.setLevel(logging.DEBUG)


def make_ca_table():

    crtmgr_db = crtmgr_database(bypass_exists=True)

    EXPECTED_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "sys_id": "TEXT",
        "name": "TEXT NOT NULL",
        "type": "TEXT NOT NULL",
        "owner": "TEXT NOT NULL",
        "days":"INT NOT NULL",
        "common_name": "TEXT",
        "created": "INT NOT NULL",
    }

    # Step 1: Create table if not exists
    crtmgr_db.insert_query(
        """
        CREATE TABLE IF NOT EXISTS certificate_authorities (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """
    )

    # Step 2: Get current columns
    existing_cols = crtmgr_db.select_query_dict("PRAGMA table_info(certificate_authorities)")
    existing_col_names = [x["name"] for x in existing_cols]

    # Step 3: Add any missing columns
    for col_name, col_def in EXPECTED_COLUMNS.items():
        if col_name not in existing_col_names:
            logging.info(f"Adding missing column: {col_name}")
            crtmgr_db.insert_query(f"ALTER TABLE certificate_authorities ADD COLUMN {col_name} {col_def}")


def make_cert_table():

    crtmgr_db = crtmgr_database(bypass_exists=True)

    EXPECTED_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "parent_ca_sys_id": "TEXT",
        "name": "TEXT NOT NULL",
        "type": "TEXT NOT NULL",
        "owner": "TEXT NOT NULL",
        "days":"INT NOT NULL",
        "created": "INT NOT NULL",
        "common_name": "TEXT",
    }

    # Step 1: Create table if not exists
    crtmgr_db.insert_query(
        """
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """
    )

    # Step 2: Get current columns
    existing_cols = crtmgr_db.select_query_dict("PRAGMA table_info(certificates)")
    existing_col_names = [x["name"] for x in existing_cols]

    # Step 3: Add any missing columns
    for col_name, col_def in EXPECTED_COLUMNS.items():
        if col_name not in existing_col_names:
            logging.info(f"Adding missing column: {col_name}")
            crtmgr_db.insert_query(f"ALTER TABLE certificates ADD COLUMN {col_name} {col_def}")


if __name__ == "__main__":
    make_ca_table()
    make_cert_table()
    parser = argparse.ArgumentParser()