import json
import toml
import uuid
import os
import logging
import subprocess
import re
import tempfile
import glob
from flask import g
from authentication import *
from sql import crtmgr_database
import shutil
import signal
import math
from threading import Thread
from config import resolve_config_file



logging.basicConfig(format="[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s", datefmt="%m/%d/%Y_%I:%M:%S")
logging.root.setLevel(logging.DEBUG)

# set up custom logging and syslog if OK
def audit_log_setup():

    conf_file = resolve_config_file("syslog")
    try:
        with open(conf_file, "r") as f:
            SYSLOG_APP_CONFIG = toml.load(f)
    except FileNotFoundError:
        SYSLOG_APP_CONFIG = {}

    send_syslog = False
    if SYSLOG_APP_CONFIG.get("syslog_config", {}).get("syslog_host", None) and SYSLOG_APP_CONFIG.get("syslog_config", {}).get("syslog_port", None):
        send_syslog = True
        logging.info("Selecting to send to server")
    if send_syslog:
        syslog_handler = logging.handlers.SysLogHandler(address=(SYSLOG_APP_CONFIG['syslog_config']['syslog_host'], int(SYSLOG_APP_CONFIG['syslog_config']['syslog_port'])))


    audit_logger = logging.getLogger("audit_log")
    audit_file_handler = logging.FileHandler("audit.log")
    audit_file_handler.setLevel(logging.INFO)
    
    
    LOG_FORMAT = '%(asctime)s certmanager %(name)s[%(process)d]: %(message)s'
    # Use a custom date format that includes the year
    DATE_FORMAT = '%b %d %Y %H:%M:%S' # e.g., Nov 06 2025 20:15:04
    
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    audit_file_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_file_handler)
    if send_syslog:
        syslog_handler.setFormatter(formatter)
        audit_logger.addHandler(syslog_handler)

    logging.info(f"Created log file: audit.log")
    
    audit_logger.info(f"Action=audit_start Send_syslog={send_syslog} Filepath={conf_file}")

    
    return audit_logger

audit_logger = audit_log_setup()

conf_file = resolve_config_file("app")
with open(conf_file, "r") as f:
    APP_CONFIG = toml.load(f)
CERT_STORAGE_FP = APP_CONFIG.get("certificate_defaults", {}).get("cert_storage")
if not CERT_STORAGE_FP:
    logging.error("No filepath for 'cert_storage'. Check config.")
    exit()

crtmgr_db = crtmgr_database()


def shutdown_thread():
    sleep_countdown = 10
    for i in range(sleep_countdown, -1, -1):
        logging.info("A SYSTEM API EXIT HAS BEEN REQUESTED. RESTARTING IN {} ... EVERYTHING WILL BE TERMINATED".format(
            i
        ))
        time.sleep(1)
    
    audit_logger.info("Action=restart_api")    
    os.kill(os.getpid(), signal.SIGINT)

def is_valid_iso_country(value):
    iso  = [
    "AD","AE","AF","AG","AI","AL","AM","AO","AQ","AR","AS","AT","AU","AW","AX","AZ",
    "BA","BB","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BV","BW","BY","BZ",
    "CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CW","CX","CY","CZ",
    "DE","DJ","DK","DM","DO","DZ",
    "EC","EE","EG","EH","ER","ES","ET",
    "FI","FJ","FK","FM","FO","FR",
    "GA","GB","GD","GE","GF","GG","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY",
    "HK","HM","HN","HR","HT","HU",
    "ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT",
    "JE","JM","JO","JP",
    "KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ",
    "LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY",
    "MA","MC","MD","ME","MF","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ",
    "NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ",
    "OM",
    "PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY",
    "QA",
    "RE","RO","RS","RU","RW",
    "SA","SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","SS","ST","SV","SX","SY","SZ",
    "TC","TD","TF","TG","TH","TJ","TK","TL","TM","TN","TO","TR","TT","TV","TZ",
    "UA","UG","UM","US","UY","UZ",
    "VA","VC","VE","VG","VI","VN","VU",
    "WF","WS",
    "YE","YT",
    "ZA","ZM","ZW"
    ]
    return bool(value in iso)

def is_vald_roles(value):
    valid = ["*", "read", "write", "manage_users"]
    for r in value:
        if not r in valid:
            return False
    return True

def run_command(command, args=None, allowed_commands=None):
    """
    Safely run a shell command with mitigations against parameter injection.

    Parameters:
        command (str): The base command to run.
        args (list[str] | None): A list of arguments to pass to the command.
        allowed_commands (list[str] | None): Optional whitelist of allowed commands.

    Returns:
        dict: { 'success': bool, 'stdout': str, 'stderr': str, 'returncode': int }
    """

    # Whitelist enforcement (if provided)
    if allowed_commands and command not in allowed_commands:
        raise ValueError(f"Command '{command}' is not allowed.")

    # Ensure args is a list
    if args is None:
        args = []

    # Convert all arguments to strings safely
    safe_args = [str(a) for a in args]

    logging.debug(f"API server is running shell command: '{command} {' '.join(safe_args)}")

    try:
        # Run command safely without using the shell
        result = subprocess.run(
            [command] + safe_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False, check=False  # Prevents shell injection  # Don’t raise automatically on error
        )

        return {"success": result.returncode == 0, "stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "returncode": result.returncode}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": f"Command '{command}' not found", "returncode": -1}
    except Exception as e:
        logging.error(f"Could not run command: {e}")
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

def has_special_chars(value):
    """
    Returns True if the value contains characters unsafe for file paths.
    """
    # Allow only letters, numbers, dash, underscore, dot
    safe_pattern = re.compile(r"^[A-Za-z0-9.*_-].+$")
    return not bool(safe_pattern.match(value))

def base_response_schema():
    return {"errors": [], "warnings": [], "result": {}}

def try_json_load(request):
    # either return the data of the loaded JSON, or a modified response
    # that the helper can directly return back to the main flask call

    resp = base_response_schema()

    try:
        data = json.loads(request.data)
        return False, data
    except:
        resp["errors"].append("request is not JSON")
        return True, resp

def calc_remaining_days(created, days):
    day = 86400
    now = int(time.time())
    expires_times = created + (days * day)
    
    if now > expires_times:
        return 0
    
    remaining = expires_times - now
    days_remaining = math.floor(remaining / day)
    return days_remaining
        
def certificate_date_status(created, days, warning_days=14):
    now = int(time.time())
    day = 86400
    days_int = days * day
    warning_time = created + ((days-warning_days) * day)
    
    if now > created + days_int:
        return "expired"
    elif now > warning_time:
        return "expiring"
    
    return "ok"
    
def create_certauthority_helper(request):

    resp = base_response_schema()
    identifier = str(uuid.uuid4())

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500

    if not data.get("keyphrase"):
        resp["errors"].append("keyphrase missing from payload")
        return resp, 500

    if not data.get("name"):
        resp["errors"].append("certificate authority must have a name")
        return resp, 500

    # get important values for key gen
    ca_name = data.get("name")
    if has_special_chars(ca_name):
        resp["errors"].append("certificate authority name contains illegal characters")
        audit_logger.error(f"Action=Reject Error=name {ca_name} contained illegal characters. Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")
        return resp, 500

    keyphrase = data.get("keyphrase")
    keysize = data.get("ca_keysize", APP_CONFIG.get("certificate_defaults", {}).get("ca_keysize"))

    # make the directory needed
    disk_basepath = os.path.join(CERT_STORAGE_FP, identifier, "ca")  # make folder for CA
    os.makedirs(disk_basepath, exist_ok=True)

    ## Generate key
    keyname_fp = os.path.join(disk_basepath, ca_name + ".key")
    # openssl genrsa -des3 -out myCA.key -passout pass:foobar 2048
    run_result = run_command("openssl", ["genrsa", "-des3", "-out", f"{keyname_fp}", "-passout", f"pass:{keyphrase}", keysize], ["openssl"])
    if not run_result["success"]:
        resp["errors"].append("failed to execute key generation")
        logging.error(f"{run_result['stderr']}")
        return resp, 500

    ## Generate the .pem file
    # openssl req -x509 -new -nodes -key myCA.key -sha256 -days 1825 -out myCA.pem
    ca_days_length = data.get("ca_days_length", APP_CONFIG.get("certificate_defaults", {}).get("ca_days_length"))
    country = data.get("country", APP_CONFIG.get("certificate_defaults", {}).get("country"))
    state = data.get("state", APP_CONFIG.get("certificate_defaults", {}).get("state"))
    locality = data.get("locality", APP_CONFIG.get("certificate_defaults", {}).get("locality"))
    organisation_name = data.get("organisation_name", APP_CONFIG.get("certificate_defaults", {}).get("organisation_name"))
    organisational_unit_name = data.get("organisational_unit_name", APP_CONFIG.get("certificate_defaults", {}).get("organisational_unit_name"))
    common_name = data.get("common_name", APP_CONFIG.get("certificate_defaults", {}).get("common_name"))
    email = data.get("email", APP_CONFIG.get("certificate_defaults", {}).get("email"))

    # sample subject
    # -subj "/C=US/ST=Springfield State/L=Springfield/O=Hellfish Media/OU=7G/CN=Hellfish Media/emailAddress=abraham@hellfish.media"
    subject = f"/C={country}/ST={state}/L={locality}/O={organisation_name}/OU={organisational_unit_name}/CN={common_name}/emailAddress={email}"

    pem_fp = os.path.join(disk_basepath, ca_name + ".pem")
    run_result = run_command(
        "openssl", ["req", "-x509", "-new", "-nodes", "-key", keyname_fp, "-sha512", "-days", ca_days_length, "-out", pem_fp, "-passin", f"pass:{keyphrase}", "-subj", f"{subject}"], ["openssl"]
    )
    if not run_result["success"]:
        resp["errors"].append("failed to execute pem generation")
        return resp, 500

    
    # save database and remove if we cannot save
    now = int(time.time())
    q = f"INSERT INTO certificate_authorities (name, type, owner, days, created, common_name, sys_id) VALUES ('{ca_name}', 'authority', '{g.username}', '{ca_days_length}', '{now}', '{common_name}', '{identifier}')"
    insert=crtmgr_db.insert_query(q)
    if not insert:
        resp["errors"].append("error saving to database")
        remove_path = os.path.join(CERT_STORAGE_FP, identifier)
        shutil.rmtree(remove_path)
        logging.error(f"Could not save ca authority with ID {identifier} to DB. Removing everything under {remove_path}")
        return resp, 500
    
    resp["result"] = {"id": identifier}
    audit_logger.info(f"Action=authority_create. Ca_name={ca_name} Ca_id={identifier} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")
    return resp, 200

def delete_certauthority_helper(ca_id):

    resp = base_response_schema()
    
    if not ca_id:
        resp["errors"]="id not supplied"
        return resp, 500

   # make the directory needed
    disk_basepath = os.path.join(CERT_STORAGE_FP, ca_id) # delete everything under ID
    if not os.path.exists(disk_basepath):
        resp['warnings'].append("file/folder path did not exist")
    else:
        shutil.rmtree(disk_basepath)
        
    q = f"DELETE FROM certificate_authorities WHERE sys_id = '{ca_id}'"
    res = crtmgr_db.insert_query(q)
    if not res:
        resp["warnings"].append("could not delete from certificate_authorities")

    q = f"DELETE FROM certificates WHERE parent_ca_sys_id = '{ca_id}'"
    res = crtmgr_db.insert_query(q)
    if not res:
        resp["warnings"].append("could not delete from certificates")
    
    if not resp["warnings"] and not resp["errors"]:
        resp["result"]={"deleted_id":ca_id}

    audit_logger.info(f"Action=authority_delete. Ca_id={ca_id} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")
    return resp, 200

def create_certificate_helper(request, ca_id):

    resp = base_response_schema()
    identifier = ca_id

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500

    if not data.get("keyphrase"):
        resp["errors"].append("keyphrase missing from payload")
        return resp, 500

    if not data.get("name"):
        resp["errors"].append("certificate must have a name")
        return resp, 500

    if not data.get("ca_name"):
        resp["errors"].append("must supply the certificate authority name as it was done on creation")
        return resp, 500

    # get important values for key gen
    overwrite = data.get("overwrite", False)
    ca_name = data.get("ca_name")
    name = data.get("name")
    if has_special_chars(name):
        resp["errors"].append("certificate name contains illegal characters")
        return resp, 500
    keyphrase = data.get("keyphrase")
    keysize = data.get("cert_keysize", APP_CONFIG.get("certificate_defaults", {}).get("cert_keysize"))

    # make the directory needed
    disk_basepath = os.path.join(CERT_STORAGE_FP, identifier)
    disk_basepath_ca = os.path.join(disk_basepath, "ca")
    disk_basepath_certs = os.path.join(disk_basepath, "certs", name)

    if not os.path.exists(os.path.join(disk_basepath_ca)):
        resp["errors"].append("the certificate authority identifier does not exist")
        return resp, 500

    if not os.path.exists(os.path.join(disk_basepath_ca, f"{ca_name}.key")):
        resp["errors"].append("the certificate authority name does not exist")
        return resp, 500

    
    ## Get subject data for the certificate
    country = data.get("country", APP_CONFIG.get("certificate_defaults", {}).get("country"))
    state = data.get("state", APP_CONFIG.get("certificate_defaults", {}).get("state"))
    locality = data.get("locality", APP_CONFIG.get("certificate_defaults", {}).get("locality"))
    organisation_name = data.get("organisation_name", APP_CONFIG.get("certificate_defaults", {}).get("organisation_name"))
    organisational_unit_name = data.get("organisational_unit_name", APP_CONFIG.get("certificate_defaults", {}).get("organisational_unit_name"))
    common_name = data.get("common_name", APP_CONFIG.get("certificate_defaults", {}).get("common_name"))
    email = data.get("email", APP_CONFIG.get("certificate_defaults", {}).get("email"))

    if not is_valid_iso_country(country):
        resp["errors"].append("invalid country")
        return resp, 500
    
    ## Generate key
    os.makedirs(disk_basepath_certs, exist_ok=True)
    keyname_fp = os.path.join(disk_basepath_certs, name + ".key")
    if os.path.exists(keyname_fp) and not overwrite:
        resp["errors"].append(f"key '{name}' exits. Specify 'overwrite: True' in the payload to continue.")
        return resp, 500

    # openssl genrsa -out hellfish.test.key 2048
    run_result = run_command("openssl", ["genrsa", "-out", f"{keyname_fp}", keysize], ["openssl"])
    if not run_result["success"]:
        resp["errors"].append("failed to execute key generation")
        logging.error(f"{run_result['stderr']}")
        return resp, 500


    # sample subject
    # -subj "/C=US/ST=Springfield State/L=Springfield/O=Hellfish Media/OU=7G/CN=Hellfish Media/emailAddress=abraham@hellfish.media"
    subject = f"/C={country}/ST={state}/L={locality}/O={organisation_name}/OU={organisational_unit_name}/CN={common_name}/emailAddress={email}"

    ## generate the CSR
    # openssl req -new -key hellfish.test.key -out hellfish.test.csr
    csr_fp = os.path.join(disk_basepath_certs, name + ".csr")
    run_result = run_command("openssl", ["req", "-new", "-key", keyname_fp, "-out", csr_fp, "-subj", f"{subject}"], ["openssl"])
    if not run_result["success"]:
        resp["errors"].append("failed to execute csr generation")
        return resp, 500

    # setup a temporary directory so we can write x509 extensions files
    temp_dir = tempfile.mkdtemp()

    extension_contents = """
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
    """

    if data.get("alternative_name", None):
        extension_contents += f"""
subjectAltName = @alt_names

[alt_names]
DNS.1 = {data.get("alternative_name")}
        """

    # start managing extensions
    extensions_fp = os.path.join(temp_dir, f"{name}.ext")
    with open(extensions_fp, "w") as f:
        f.write(extension_contents)

    logging.debug(f"Using {extensions_fp} as the temporary extensions file")

    # openssl x509 -req -in hellfish.test.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial -out hellfish.test.crt -days 825 -sha256 -extfile hellfish.test.ext
    certificate_days_length = data.get("cert_days_length", APP_CONFIG.get("certificate_defaults", {}).get("cert_days_length"))
    cert_out_fp = os.path.join(disk_basepath_certs, name + ".crt")

    run_result = run_command(
        "openssl",
        [
            "x509",
            "-req",
            "-in",
            csr_fp,
            "-CA",
            os.path.join(disk_basepath_ca, f"{ca_name}.pem"),
            "-CAkey",
            os.path.join(disk_basepath_ca, f"{ca_name}.key"),
            "-CAcreateserial",
            "-out",
            cert_out_fp,
            "-days",
            certificate_days_length,
            "-passin",
            f"pass:{keyphrase}",
            "-extfile",
            extensions_fp,
            "-sha256",
        ],
        ["openssl"],
    )
    if not run_result["success"]:
        resp["errors"].append("Failed to execute pem generation. Potentially caused by incorrect keyphrase supplied for authority certificate.")
        logging.error(f"{run_result['stderr']}")
        audit_logger.error(f"Action=possible_pem_passkey_mismatch. Ca_name={ca_name} Ca_id={identifier} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

        # clean up
        if os.path.exists(keyname_fp):
            os.remove(keyname_fp)        
        return resp, 500

    # save database and remove if we cannot save
    now = int(time.time())
    q = f"INSERT INTO certificates (name, type, owner, days, created, common_name, parent_ca_sys_id) VALUES ('{name}', 'cert', '{g.username}', '{certificate_days_length}', '{now}', '{common_name}', '{identifier}')"
    insert=crtmgr_db.insert_query(q)
    if not insert:
        resp["errors"].append("error saving to database")
        remove_path = os.path.join(disk_basepath_certs)
        shutil.rmtree(remove_path)
        logging.error(f"Could not save certificate with name {name} and authority with ID {identifier} to DB. Removing everything under {remove_path}")
        
        # clean up
        if os.path.exists(keyname_fp):
            os.remove(keyname_fp)
        return resp, 500


    cert_key = ""
    cert_cert = ""

    with open(cert_out_fp, "r") as f:
        cert_cert = f.read()

    with open(keyname_fp, "r") as f:
        cert_key = f.read()

    resp["result"] = {"key": cert_key, "cert":cert_cert}
    audit_logger.info(f"Action=certificate_create Cert_name={name} Ca_name={ca_name} Ca_id={identifier} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def delete_certificate_helper(ca_id, cert_name):

    resp = base_response_schema()
    
    if not ca_id:
        resp["errors"]="id not supplied"
        return resp, 500

   # make the directory needed
    disk_basepath = os.path.join(CERT_STORAGE_FP, ca_id, "certs", cert_name) # delete everything under ID
    if not os.path.exists(disk_basepath):
        resp['warnings'].append("file/folder path did not exist")
    else:
        shutil.rmtree(disk_basepath)
        

    q = f"DELETE FROM certificates WHERE parent_ca_sys_id = '{ca_id}' AND name = '{cert_name}'"
    res = crtmgr_db.insert_query(q)
    if not res:
        resp["warnings"].append("could not delete from certificates")
    
    if not resp["warnings"] and not resp["errors"]:
        resp["result"]={"deleted_id":ca_id}
    
    audit_logger.info(f"Action=certificate_delete Cert_name={cert_name} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def download_certificate_helper(ca_id, cert_name):

    resp = base_response_schema()
    identifier = ca_id


    # get important values for key gen

    # make the directory needed
    disk_basepath = os.path.join(CERT_STORAGE_FP, identifier)
    disk_basepath_certs = os.path.join(disk_basepath, "certs", cert_name)

    cert_out_fp = os.path.join(disk_basepath_certs, f"{cert_name}.crt")
    keyname_fp = os.path.join(disk_basepath_certs, f"{cert_name}.key")
        
    if not os.path.exists(cert_out_fp) or not os.path.exists(keyname_fp):
        resp["errors"].append(f"Could not find keys under name '{cert_name}'")
        return resp, 500
        

    cert_key = ""
    cert_cert = ""

    with open(cert_out_fp, "r") as f:
        cert_cert = f.read()

    with open(keyname_fp, "r") as f:
        cert_key = f.read()

    resp["result"] = {"key": cert_key, "cert":cert_cert}
    audit_logger.info(f"Action=certificate_download Cert_name={cert_name} Ca_id={identifier} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def download_certauthority_helper(ca_id):

    resp = base_response_schema()
    identifier = ca_id

    disk_basepath = os.path.join(CERT_STORAGE_FP, identifier)
    files = glob.glob(os.path.join(disk_basepath, "ca", "*.pem"))
    print(files,os.path.join(disk_basepath, "*.pem"))
    
    if not files:
        resp["errors"].append(f"Could not find certificate authority under id '{identifier}'")
        return resp, 500
        
    cert_cert = ""

    with open(files[0], "r") as f:
        cert_cert = f.read()

    resp["result"] = {"cert":cert_cert}
    return resp, 200

def list_certauthority_helper():
    resp = base_response_schema()
    
    q = "SELECT id, name, type, owner, days, created, common_name, sys_id FROM certificate_authorities"
    results = crtmgr_db.select_query_dict(query=q)
    
    for r in results:
        r["status"]=certificate_date_status(r.get("created", 0), r.get("days", 0))
        r["remaining_days"]=calc_remaining_days(r.get("created", 0), r.get("days", 0))

    resp['result'] = results
    audit_logger.info(f"Action=authority_list Returned_results={len(results)} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def list_certificates_helper():
    resp = base_response_schema()
    
    q = """
    SELECT 
    c.id, 
    c.name, 
    c.type, 
    c.owner, 
    c.days, 
    c.created, 
    c.common_name, 
    c.parent_ca_sys_id,
    ca.common_name AS ca_common_name
    FROM certificates c
    JOIN (
        SELECT sys_id, common_name
        FROM certificate_authorities
    ) ca
    ON c.parent_ca_sys_id = ca.sys_id;
    """
    results = crtmgr_db.select_query_dict(query=q)
    
    for r in results:
        r["status"]=certificate_date_status(r.get("created", 0), r.get("days", 0))
        r["remaining_days"]=calc_remaining_days(r.get("created", 0), r.get("days", 0))

    resp['result'] = results
    audit_logger.info(f"Action=certificate_list Returned_results={len(results)} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def user_login_helper(request, short:False):
    # set g.src ip here. Normally would get done through @authentication_required 
    # however, unauthenticated users can access this call so is not populated
    
    g.src_ip = get_src_ip(request)
    g.user_agent = get_user_agent(request)
    
    
    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500
    
    resp = base_response_schema()

    if not data.get("username"):
        resp['errors'].append("username not supplied")
        return resp, 500

    if not data.get("password"):
        resp['errors'].append("password not supplied")
        return resp, 500        
    
    username = data['username']
    password = data['password']
    
    login_result = user_login(username, password, short_token=short)
    if not login_result['success']:
        resp["errors"].append(login_result['data'])
        audit_logger.error(f"Action=password_fail Username={username} Ip={g.src_ip} Useragent={g.user_agent}")

        return resp, 403
    
    resp['token']=login_result['data']
    audit_logger.info(f"Action=password_success Username={username} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200
    
def user_resetpassword_helper(request, for_user):

    resp = base_response_schema()

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 400

    if not data.get("password"):
        resp["errors"].append("password missing from payload")
        return resp, 400

    if not data.get("new_password"):
        resp["errors"].append("new_password missing from payload")
        return resp, 400

    # see if user is valid
    q = "SELECT username FROM users WHERE username = ?"
    user_record = crtmgr_db.select_query_dict(query=q, params=(for_user,))
    if not user_record:
        resp["errors"].append("user specified does not exist")
        audit_logger.error(f"Action=password_reset Error=not_exists Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

        return resp, 400
    
    if len(data.get("new_password")) < 8:
        resp["errors"].append("new password too short")
        return resp, 400
    
    # try a login so we know 
    login_result = user_login(g.username, data.get("password"))
    if not login_result['success']:
        resp["errors"].append(login_result['data'])
        return resp, 403
    
    new_salt = gen_salt()
    pass_hash = secure_hash_password(plain_text=data.get("new_password"), pass_salt=new_salt)
    
    q = f"UPDATE users SET password_hash = '{pass_hash}', password_salt= '{new_salt}' WHERE username = '{for_user}'"
    insert=crtmgr_db.insert_query(q)
    if not insert:
        resp["errors"].append("could not update db")
        return resp, 500
    
    # catch all means we've been successful
    audit_logger.info(f"Action=password_reset Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    resp["result"]=True
    return resp, 200

def user_create_helper(request, for_user):

    resp = base_response_schema()

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500

    if not data.get("username"):
        resp["errors"].append("username missing from payload")
        return resp, 500

    if not data.get("roles"):
        resp["errors"].append("roles must be present")
        return resp, 500
    
    q = "SELECT username, roles, created FROM users WHERE type='user' AND username = ? "
    user_record = crtmgr_db.select_query_dict(query=q, params=(for_user,))
    user_record = user_record[0]
    user_roles = user_record.get("roles", '[]')
    user_roles = json.loads(user_roles)
    compare_roles = data.get("roles", [])
    if len(compare_roles) == 0 or not isinstance(compare_roles, list):
        resp["errors"].append("roles supplied empty or not list")
        return resp, 500
    
    # see if the user is trying to create a token that is beyond their exisitng 
    # role scope
    compare_issues=[]
    for role in compare_roles:
        if role not in user_roles and "*" not in user_roles:
            compare_issues.append(f"source user does not have {role} to assign")
    
    if compare_issues:
        resp["errors"]=compare_issues
        return resp, 401
    
    # check if the user already exists
    q = "SELECT username, roles, created FROM users WHERE type='user' AND username = ? "
    user_record = crtmgr_db.select_query_dict(query=q, params=(data['username'],))
    if user_record:
        resp["errors"].append("username already exists")
        return resp, 500


    # generate authentication
    username = data.get("username")
    new_password = gen_salt()
    new_salt = gen_salt()
    roles = data.get("roles")
    now = int(time.time())
    password_hash = secure_hash_password(new_password, new_salt)
    
    # roles check
    if not is_vald_roles(roles):
        resp["errors"].append("invalid role supplied")
        return resp, 500   
        
    
    # insert record
    q = f"INSERT INTO users (username, password_hash, type, created, password_salt, roles) VALUES ('{username}', '{password_hash}', 'user', '{now}', '{new_salt}', '{json.dumps(roles)}')"
    inserted = crtmgr_db.insert_query(q)
    if not inserted:
        resp["errors"].append("could not save record exists")
        return resp, 500   

    # successful
    audit_logger.info(f"Action=user_create Created_user={username} Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    resp["result"]["password"] = new_password
    return resp, 200

def user_details_helper(for_user):
    resp = base_response_schema()

    if not for_user:
        resp["errors"].append("request missing for_user")
        return resp, 401


    params = ()
    if for_user == "*":
        q = "SELECT username, roles, owner, created FROM users WHERE type='user'"
    else:
        q = "SELECT username, roles, owner, created FROM users WHERE username= ?"
        params = (for_user,)
            
    user_record = crtmgr_db.select_query_dict(query=q, params=params)
    if not user_record:
        resp["warnings"].append("empty results - likely malformed request")
        user_record=[]
        
    
    resp["result"]["users"]=user_record
    audit_logger.info(f"Action=user_details_get Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    
    return resp, 200   

def apikeys_details_helper(for_user):
    resp = base_response_schema()

    if not for_user:
        resp["errors"].append("request missing for_user")
        return resp, 401

    params = ()
    if for_user == "*":
        q = "SELECT username, roles, created FROM users WHERE type='api'"
    else:
        q = "SELECT username, roles, created FROM users WHERE owner= ? AND type='api'"
        params = (for_user,)
        
            
    user_record = crtmgr_db.select_query_dict(query=q, params=params)
    if not user_record:
        resp["warnings"].append("empty results - likely malformed request")
        user_record=[]
        
    
    resp["result"]["users"]=user_record
    audit_logger.info(f"Action=user_list_api_keys Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200       

def user_apikeys_create_helper(request, for_user):
    resp = base_response_schema()
    identifier = str(uuid.uuid4())+f"@{for_user}"

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500

    if not data.get("roles"):
        resp["errors"].append("roles missing from payload")
        return resp, 500

    if not data.get("days_expiry") or not isinstance(data['days_expiry'], int):
        resp["errors"].append("days_expiry must be supplied")
        return resp, 500
    

    q = "SELECT username, roles, created FROM users WHERE type='api' AND username = ?"
    user_record = crtmgr_db.select_query_dict(query=q, params=(identifier,))
    if user_record:
        resp["errors"].append("key clash on creation - please resubmit request")
        return resp, 500
    
    # check we are not an API instance, trying to create another API key
    q = "SELECT username, roles, created FROM users WHERE type='api' AND username = ? "
    user_record = crtmgr_db.select_query_dict(query=q, params=(for_user,))
    if user_record:
        resp["errors"].append("You cannot use an API key to create new API keys")
        return resp, 401
    
    # get users current roles
    q = "SELECT username, roles, created FROM users WHERE type='user' AND username = ? "
    user_record = crtmgr_db.select_query_dict(query=q, params=(for_user,))
    user_record = user_record[0]
    user_roles = user_record.get("roles", '[]')
    user_roles = json.loads(user_roles)
    compare_roles = data.get("roles", [])
    if len(compare_roles) == 0 or not isinstance(compare_roles, list):
        resp["errors"].append("roles supplied empty or not list")
        return resp, 500
    
    # see if the user is trying to create a token that is beyond their exisitng 
    # role scope
    compare_issues=[]
    for role in compare_roles:
        if role not in user_roles and "*" not in user_roles:
            compare_issues.append(f"source user does not have {role} to assign")
    
    if compare_issues:
        resp["errors"]=compare_issues
        return resp, 401
    
    
    day = 86400
    ttl = day * data.get("days_expiry")
    now = int(time.time())
    expire_time = now + ttl
    
    
    max_keys = APP_CONFIG.get("auth", {}).get("max_api_keys_user", 5)
    q = "SELECT username, roles, created FROM users WHERE type='api' AND owner = ? AND expires > ?"
    api_records = crtmgr_db.select_query_dict(query=q, params=(for_user, now,))
    if len(api_records) > max_keys:
        resp["errors"].append("exceeded API keys for user")
        return resp, 402
    
    
    q = "INSERT INTO users (username, type, created, expires, roles, owner) VALUES (?, 'api', ?, ?, ?, ?)"
    params = (identifier ,now, expire_time, json.dumps(data.get('roles', [])), for_user)
    insert = crtmgr_db.insert_query(q, params=params)
    if not insert:
        resp["errors"].append("issue saving new API key to db")
        return resp, 500
    
    
    secret = APP_CONFIG.get("jwt", {}).get("secret", "")
    alg = APP_CONFIG.get("jwt", {}).get("alg", "HS256")
    jwt = create_jwt(username=identifier, secret=secret, alg=alg)
    resp["result"]["token"]=jwt
    audit_logger.info(f"Action=user_create_api_keys Id={identifier} Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def user_apikeys_list_helper(for_user):
    resp = base_response_schema()
    
    now = int(time.time())
    q = "SELECT username, roles, created, expires FROM users WHERE type='api' AND owner = ? AND expires > ?"
    keys = crtmgr_db.select_query_dict(query=q, params=(for_user, now, ))
    if not keys:
        keys = []
        
    resp["result"]["keys"]=keys
    audit_logger.info(f"Action=user_api_keys_list Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200    

def user_apikeys_delete_keyid_helper(for_user, keyid):
    resp = base_response_schema()

    q = f"DELETE FROM users WHERE username = ? AND owner = ?"
    res = crtmgr_db.insert_query(q, params=(keyid, for_user))
    if not res:
        resp["warnings"].append("could not delete from certificates")
        return resp, 500
    
    resp["result"]=True
    audit_logger.info(f"Action=user_delete_api_keys Id={keyid} Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def user_profile_update_helper(request, for_user, source_user):
    resp = base_response_schema()

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500
    
    q = "SELECT username, roles, created FROM users WHERE type='user' AND username = ? "
    user_record = crtmgr_db.select_query_dict(query=q, params=(for_user,))
    if not user_record:
        resp["errors"].append("User does not exist")
        return 400
    
    if for_user == "manager":
        resp["errors"].append("manager is a built in user and cannot be modified")
        logging.warning("Attempt to update 'manager' user. Should not occur, possible bad actor?")
        return resp, 400

    def run_insert(q):
        insert=crtmgr_db.insert_query(q)
        if not insert:
            return False
        return True
        
    
    # process role checks - only currently supported
    if data.get("roles"):
            
        # get source users current roles
        q = "SELECT username, roles, created FROM users WHERE type='user' AND username = ? "
        user_record = crtmgr_db.select_query_dict(query=q, params=(source_user,))
        user_record = user_record[0]
        user_roles = user_record.get("roles", '[]')
        user_roles = json.loads(user_roles)
        new_roles = data.get("roles", [])
        
        # check submitted
        if len(user_roles) == 0 or not isinstance(user_roles, list):
            resp["errors"].append("roles supplied empty or not list")
            return resp, 500
   
        if not is_vald_roles(data.get("roles", [])):
            resp["errors"].append("manager is a built in user and cannot be modified")
            return resp, 400
        
        # see if the user is trying to create a token that is beyond their exisitng 
        # role scope
        compare_issues=[]
        for role in new_roles:
            if role not in user_roles and "*" not in user_roles:
                compare_issues.append(f"source user does not have {role} to assign")
        
        if compare_issues:
            audit_logger.info(f"Action=update_user Error={compare_issues} Username={g.username} Target_user={for_user}")

            resp["errors"]=compare_issues
            return resp, 401
        
        # if we reach this far, we are successful
        q = f"UPDATE users SET roles = '{json.dumps(new_roles)}' WHERE username = '{for_user}'"
        if not run_insert(q):
            resp["errors"].append("cannot update DB")
            return resp, 500
        else:
            audit_logger.info(f"Action=update_user_roles Roles={new_roles} Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")


    # return success
    return resp, 200

def user_profile_delete_helper(for_user, source_user):
    resp = base_response_schema()
    
    if for_user == "manager":
        resp["errors"].append("'manager' in a built in account and cannot be removed.")
        return resp, 400   
 
    if source_user == for_user:
        resp["errors"].append("User cannot delete their own account. User another user or manager account.")
        return resp, 400   
     

    
    
    q = f"DELETE FROM users WHERE username = '{for_user}' OR owner = '{for_user}'"
    res = crtmgr_db.insert_query(q)
    if not res:
        resp["warnings"].append("could not delete user entries")
        return resp, 500
    
    resp["result"]["deleted_user"] = for_user
    # return success
    audit_logger.info(f"Action=user_delete Username={g.username} Target_user={for_user} Ip={g.src_ip} Useragent={g.user_agent}")

    return resp, 200

def system_logs_helper(stream=False):
    resp = base_response_schema()
    logfile = "audit.log"
    
    if not os.path.exists(logfile):
        resp["errors"].append("server log not on disk")
        return resp, 500     
        
    if not stream:
        with open(logfile, "r") as f:
            resp["result"]["log"] = f.read()
            return resp, 200
        
    if stream:
        def streamer():
            try:
                with open(logfile, "r") as f:
                    while True:
                        yield f.read()
                        time.sleep(0.2)
            except FileNotFoundError:
                    yield "no_output_file"
        
        for l in streamer():
            resp["result"]["log"] = l
            return resp, 200
        
def system_logs_syslog_helper(request):
    global audit_logger
    resp = base_response_schema()

    has_errors, data = try_json_load(request)
    if has_errors:
        return data, 500
    
    if not data.get("host") or not data.get("port"):
        logging.error("required fields host/port not submitted")
        resp["errors"].append("required fields host/port not submitted")
        return resp, 400
    
    config_file = resolve_config_file("syslog")
    new_config = {
        "syslog_config":{
            "syslog_host":str(data.get("host")),
            "syslog_port":str(data.get("port"))
            }
        }
    with open(config_file, 'w') as f:
        toml.dump(new_config, f)
        
    audit_logger = audit_log_setup()
    audit_logger.info(f"Action=update_syslog Config={new_config} Username={g.username} Ip={g.src_ip} Useragent={g.user_agent}")
    resp["result"]=new_config
    
    
    # restart
    detached_playbook_thread = Thread(target=shutdown_thread)
    detached_playbook_thread.start()
    
    
    return resp, 200

