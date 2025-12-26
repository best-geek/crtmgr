import argparse
import os
import logging
from cert_meta import make_ca_table, make_cert_table
from config import resolve_config_file
from authentication import make_user_table, create_admin_user, gen_salt
from sql import crtmgr_database

import toml
import shutil

logging.basicConfig(format="[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s", datefmt="%m/%d/%Y_%I:%M:%S")
logging.root.setLevel(logging.INFO)

CONF_FILE = resolve_config_file("app")
logging.info(f"Resolved config file to: {CONF_FILE}")


def db_exists():
    db = crtmgr_database(bypass_exists=True)
    fp = db.resolve_db_filepath()
    return bool(os.path.exists(fp))


def main(in_dckr=False):
    
    toml_edited = False # indicate if it should be dumped at the end of main()
    fresh_setup =  not db_exists()
    logging.info(f"Fresh setup: {fresh_setup}")
    
    # make ca and cert tables
    make_cert_table()
    make_ca_table()
    
    # make users and set password
    make_user_table()

    
    # open conf file
    try:
        with open(CONF_FILE, "r") as f:
            APP_CONFIG = toml.load(f)
    except:
        logging.error(f"Could not load app config. Fatal error. Config file: {CONF_FILE}")
        exit()
    
    # set a random secret in the config. Will expire anything existing.
    if fresh_setup:
        logging.info("Setting up JWT salt")
        jwt_secret = gen_salt()
        APP_CONFIG['jwt']['secret'] = jwt_secret
        toml_edited = True

            
    # set admin password
    if fresh_setup:
        manager_password = create_admin_user()    
        logging.info(f"Set web UI password for 'manager' user to: {manager_password}")
        
    # edit the toml to store certificates in a location managed by docker-compose
    if in_dckr and fresh_setup:
        APP_CONFIG["certificate_defaults"]["cert_storage"] = "/persistent/cert_store"
        toml_edited = True
            

        
    # write back changes
    if toml_edited:
        with open(CONF_FILE, 'w') as f:
            toml.dump(APP_CONFIG, f)
    
    # indicate if we should restart via true
    should_restart = False
    if toml_edited: should_restart = True
    return should_restart
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-admin", help="reset the 'manager' user password",action='store_true')
    parser.add_argument("--full", help="Run through full re-installation",action='store_true')
    parser.add_argument("--container", help="Indicate the setup is occurring in a container to execute specific setup actions.",action='store_true')


    args = parser.parse_args()
    
    if args.reset_admin:
        create_admin_user()
        
    if args.full:
        restart_required  = main(in_dckr=args.container)
        if restart_required: 
            logging.info("Issuing non-zero exit code to force container restart")
            exit(1)
        
