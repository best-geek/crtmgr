import sqlite3
from os import environ
from os import path
from sys import exit
import logging
from datetime import datetime

logging.basicConfig(format="[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s", datefmt="%m/%d/%Y_%I:%M:%S")
logging.root.setLevel(logging.INFO)

class crtmgr_database():
    
    def check_exists(self, bypass, filename):
        if not bypass:
            if not path.exists(filename):
                logging.error(f"{filename} does not exist. Please run 'make_schema.py'")
                raise FileNotFoundError('File not found. Change environment for CERT_DB_FP or run make_schema.py')
    
    def __init__(self, bypass_exists=False):
        self.db_filename="crtmgr.db"
        self.check_exists(bypass_exists, self.resolve_db_filepath())
        
        
    def resolve_db_filepath(self):
        if environ.get('CERT_DB_FP') is not None:
            logging.info("Resolved database location from CERT_DB_FP")
            return environ.get('CERT_DB_FP')
        else:
            return self.db_filename
        
    def sanitize(self, value):
        return value.replace('\x00', '')
    
    def log_event(self, comment):
        now = datetime.now().isoformat()
        q=f"INSERT INTO activity_log (created_at, message) VALUES ('{now}', '{comment}')"
        self.insert_query(q)
        
    
    
    def insert_query(self,query, ignore_exists=False):
        con = sqlite3.connect(self.resolve_db_filepath())
        cur = con.cursor()
        query = self.sanitize(query)
        try:
            cur.execute(query)
            con.commit()
            logging.debug(f"Successful SQL insert - {query}")
            return True
        except Exception as e:
            if  str(e).endswith("already_exists") and ignore_exists:
                logging.debug(f"Successful SQL insert - {query}")
                return True
            else:
                logging.error(f"Failed SQL insert [error: {e}] - {query}")
                return False
    
    def select_query_dict(self, query, params=()):
            conn = sqlite3.connect(self.resolve_db_filepath())
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            cursor = conn.cursor()

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert sqlite3.Row objects to plain dicts
            dict_rows = []
            dict_rows = [dict(row) for row in rows]

            conn.close()
            return dict_rows
    
    def select_query(self, query):
        query = self.sanitize(query)
        conn = sqlite3.connect(self.resolve_db_filepath())
        cursor = conn.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            return rows
        else:
            return []

        
    