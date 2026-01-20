import pytest
import threading
import time
import os
import requests
import toml
from jsonschema import validate, ValidationError

# setup API
API_PORT = 9999
API_URL = f"http://localhost:{API_PORT}"
API_DB_FP = os.path.join("/tmp", "crtmgr.db")
LOCAL_API_CONFIG = "config.conf"
TEMP_API_CONFIG = os.path.join("/tmp","config.conf")
API_CURRENT_SESSION_TOKEN = "" # will get set later
AUTHENTICATION_STORE = {} # tests will populate this. [username] = {}. [username][password] will be populated here too.
BASE_CA_PASSWORD = "123Password!" # use this for any CA creation in tests


# modify the storage location, taking a copy of existing config
APP_CONFIG = {}
with open(LOCAL_API_CONFIG, "r") as f:
    APP_CONFIG = toml.load(f)       
APP_CONFIG["certificate_defaults"]["cert_storage"] = os.path.join("/tmp")
with open(TEMP_API_CONFIG, 'w') as f:
    toml.dump(APP_CONFIG, f)


# setup for threads before calling api_thread(). 
if os.path.exists(API_DB_FP): os.remove(API_DB_FP)
os.environ["CERT_DB_FP"] = API_DB_FP
os.environ["CONF_APP"] = TEMP_API_CONFIG

# now import custom functions that we're ready with env set
from full_setup import main as setupmain 
from full_setup import create_admin_user
setupmain()

# db exits, config modified, and env vars in place. We can now import!
from api_server import app

def api_thread(app):
    app.run(
        host="0.0.0.0",
        port=API_PORT,
        debug=False,
        use_reloader=False  # IMPORTANT when running in a thread
    )

# the decorator keeps our API active throughout the session
@pytest.fixture(scope="session", autouse=True)
def start_api():
    thread = threading.Thread(
        target=api_thread,
        args=(app,),
        daemon=True
    )
    thread.start()


    yield

def get_auth_token(username, password):
    data = {"username":  username, "password":password}
    r = requests.post(f"{API_URL}/user/login/", json=data)
    assert r.status_code == 200
    reply = r.json()
    return reply["token"]


#  -------------
# | TESTS START |
#  -------------

 
def test_api_start():
    r = requests.get(f"{API_URL}/")
    assert r.status_code == 200

def test_set_manager_token():
    global API_CURRENT_SESSION_TOKEN
    global AUTHENTICATION_STORE
    
    manager_password = create_admin_user()
    AUTHENTICATION_STORE["manager"] = {}
    AUTHENTICATION_STORE["manager"]["password"] = manager_password
    
    data = {"username": "manager", "password":manager_password}
    r = requests.post(f"{API_URL}/user/login/", json=data)
    reply = r.json()
    API_CURRENT_SESSION_TOKEN = reply["token"]
    assert API_CURRENT_SESSION_TOKEN.startswith("ey")
    
def test_account_creation():
    global AUTHENTICATION_STORE
    
    permissions = ["read", 'write', "manage_users"]
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    
    for user in permissions:
        data = {"username":user,"roles":[user]}
        r = requests.post(f"{API_URL}/user/create/", headers=headers, json=data)
        print(r.text)
        assert r.status_code == 200
        reply = r.json()
        AUTHENTICATION_STORE[user]={}
        AUTHENTICATION_STORE[user]["password"] = reply["result"]["password"]

def test_login_sqli():
    # tests a previous bug fix
    data = {"username":"manager' OR 1=1--", "password":"xxxxxxx"}
    r = requests.post(f"{API_URL}/user/login/", json=data)
    assert r.status_code != 200 # we have not been successful
    
def test_ca_cert_creation():
    cert_create_count = 100 # create 100 certs after CA is created.
    
    
    authority_name = "ca_unittest01"
    
    data = {
    "keyphrase":BASE_CA_PASSWORD,
    "name":authority_name,
    "ca_keysize":4096,
    "ca_days_length":5,
    "email":"admin@domain.com"
    }
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.post(f"{API_URL}/create/certauthority/", headers=headers, json=data)
    print(r.status_code, r.text)
    reply = r.json()
    assert "-" in reply['result']['id']

    
    ca_id = reply['result']['id']
    
    for i in range(0, cert_create_count):
    
        data = {
        "keyphrase": BASE_CA_PASSWORD,
        "name": f"unit_test_{i}",
        "ca_name": authority_name,
        "common_name": "google.com",
        "organisation_name": "Somehthing",
        "organisational_unit_name": "dasdasdas",
        "email": "sdasdasd",
        "locality": "dadasdasd",
        "state": "adsasda",
        "country": "US",
        "overwrite":True
        }
        r = requests.post(f"{API_URL}/create/certificate/{ca_id}/", headers=headers, json=data)
        reply = r.json()
        assert "-----BEGIN CERTIFICATE-----" in reply["result"]["cert"]
        assert "-----BEGIN PRIVATE KEY-----" in reply["result"]["key"]
    
def test_list_ca():
    # create at least one cert before running this test
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certauthority/", headers=headers)
    reply = r.json()
    
    
    schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Generated schema for Root",
    "type": "object",
    "properties": {
        "common_name": {
        "type": "string"
        },
        "created": {
        "type": "number"
        },
        "days": {
        "type": "number"
        },
        "id": {
        "type": "number"
        },
        "name": {
        "type": "string"
        },
        "owner": {
        "type": "string"
        },
        "remaining_days": {
        "type": "number"
        },
        "status": {
        "type": "string"
        },
        "sys_id": {
        "type": "string"
        },
        "type": {
        "type": "string"
        }
    },
    "required": [
        "common_name",
        "created",
        "days",
        "id",
        "name",
        "owner",
        "remaining_days",
        "status",
        "sys_id",
        "type"
    ]
    }
    
    
    data = reply["result"][0]
    print(data)
    success = False
    try:
        validate(instance=data, schema=schema)
        success = True
    except ValidationError as e:
        raise ValueError(f"Response does not match schema: {e.message}")
    
    assert success

def test_list_cert():
    
    # create at least one cert before running this test
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certificates/", headers=headers)
    reply = r.json()
    
    
    schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Generated schema for Root",
    "type": "object",
    "properties": {
        "ca_common_name": {
        "type": "string"
        },
        "common_name": {
        "type": "string"
        },
        "created": {
        "type": "number"
        },
        "days": {
        "type": "number"
        },
        "id": {
        "type": "number"
        },
        "name": {
        "type": "string"
        },
        "owner": {
        "type": "string"
        },
        "parent_ca_sys_id": {
        "type": "string"
        },
        "remaining_days": {
        "type": "number"
        },
        "status": {
        "type": "string"
        },
        "type": {
        "type": "string"
        }
    },
    "required": [
        "ca_common_name",
        "common_name",
        "created",
        "days",
        "id",
        "name",
        "owner",
        "parent_ca_sys_id",
        "remaining_days",
        "status",
        "type"
    ]
    }
        
    
    data = reply["result"][0]
    print(data)
    success = False
    try:
        validate(instance=data, schema=schema)
        success = True
    except ValidationError as e:
        raise ValueError(f"Response does not match schema: {e.message}")
    
    assert success
    
def test_currently_loggedin_details():
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/user/details/me/", headers=headers)
    reply = r.json()
    assert reply["result"]["users"][0]["username"] == "manager"

def test_create_list_api_key():
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    
    
    data = {
    "days_expiry":365,
    "roles":["*"]
    }
    r = requests.post(f"{API_URL}/user/apikeys/create/", headers=headers, json=data)
    reply = r.json()
    assert "ey" in reply["result"]["token"]
    
    
    # test we have inserted it
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/user/apikeys/list/", headers=headers)
    reply = r.json()
    data = reply["result"]["keys"][0]
    
    schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Generated schema for Root",
    "type": "object",
    "properties": {
        "created": {
        "type": "number"
        },
        "expires": {
        "type": "number"
        },
        "roles": {
        "type": "string"
        },
        "username": {
        "type": "string"
        }
    },
    "required": [
        "created",
        "expires",
        "roles",
        "username"
    ]
    }
    success = False
    try:
        validate(instance=data, schema=schema)
        success = True
    except ValidationError as e:
        raise ValueError(f"Response does not match schema: {e.message}")
    
    assert success

def test_create_overpermissive_api_key():
    
    
    user_token = get_auth_token("read", AUTHENTICATION_STORE["read"]["password"])

    headers = {"authorization":f"Bearer {user_token}"}
    
    # read will not have * to give
    data = {
    "days_expiry":365,
    "roles":["*"]
    }
    r = requests.post(f"{API_URL}/user/apikeys/create/", headers=headers, json=data)
    reply = r.json()
    print(reply)
    assert "source user does not have * to assign" in reply["errors"]
   
def test_certificate_get_buffered():
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certificates/", headers=headers)
    reply = r.json()
    
    cert_meta = reply["result"][0]
    # parent_ca_sys_id
    # download/certauthority/53f7a66f-581f-42af-a5fb-5b762a8f0604?buffer=true
    download_url = f"{API_URL}/download/certificate/{cert_meta['parent_ca_sys_id']}/{cert_meta['name']}/?buffer=true"
    r = requests.get(download_url, headers=headers)
    assert r.text.startswith("PK") and ".key" in r.text

def test_api_create_over_permissive():
    user_token = get_auth_token("read", AUTHENTICATION_STORE["read"]["password"])
    headers = {"authorization":f"Bearer {user_token}"}

    # read doest not have this permission to assign and should error.
    data = {
    "days_expiry":365,
    "roles":["*"]
    }
    
    
    r = requests.post(f"{API_URL}/user/apikeys/create/", headers=headers, json=data)
    reply = r.json()
    assert r.status_code == 401 and "source user does not have * to assign" in r.text
    
def test_read_permissions_work():
    
    against_users = ["write", "manage_users"]
    for u in against_users:
    
        user_token = get_auth_token(u, AUTHENTICATION_STORE[u]["password"])
        headers = {"authorization":f"Bearer {user_token}"}


        # write does not have permissions to view
        r = requests.get(f"{API_URL}/list/certificates/", headers=headers)
        reply = r.json()
        assert "invalid permissions" in reply["errors"] 

def test_password_change():
    global AUTHENTICATION_STORE
    
    new_password = "abc123456"
    current_password = AUTHENTICATION_STORE["write"]["password"]
    
    user_token = get_auth_token("write", current_password)
    headers = {"authorization":f"Bearer {user_token}"}

    data = {
        "password": current_password,
        "new_password": new_password
    }
    
    r = requests.post(f"{API_URL}/user/resetpassword/write", headers=headers, json=data)
    assert r.status_code == 200
    
    AUTHENTICATION_STORE["write"]["password"] = new_password
    user_token = get_auth_token("write", new_password)

def test_incorrect_login_password():
    
    data = {"username":  "write", "password":"xyz1234"}
    r = requests.post(f"{API_URL}/user/login/", json=data)
    assert r.status_code == 403
    
def test_write_over_permissive():
    
    # have to get CA data first
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certauthority/", headers=headers)
    reply = r.json()
    ca_meta = reply["result"][0]
    ca_name = ca_meta["name"]
    ca_id = ca_meta["sys_id"]

    
    # none of these users should be able to write
    against_users = ["read", "manage_users"]
    for u in against_users:
        print(f"testing for: {u}")
    
        user_token = get_auth_token(u, AUTHENTICATION_STORE[u]["password"])
        headers = {"authorization":f"Bearer {user_token}"}
        
        data = {
        "keyphrase": BASE_CA_PASSWORD,
        "name": "unit_test01",
        "ca_name": ca_name,
        "common_name": "google.com",
        "organisation_name": "Somehthing",
        "organisational_unit_name": "dasdasdas",
        "email": "sdasdasd",
        "locality": "dadasdasd",
        "state": "adsasda",
        "country": "US",
        "overwrite":True
        }
        r = requests.post(f"{API_URL}/create/certificate/{ca_id}/", headers=headers, json=data)

        print(r.text)
        reply = r.json()
        assert "invalid permissions" in reply["errors"]  

def test_cert_ca_keyphrase_validation():
    
    # have to get CA data first
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certauthority/", headers=headers)
    reply = r.json()
    ca_meta = reply["result"][0]
    ca_name = ca_meta["name"]
    ca_id = ca_meta["sys_id"]

        
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    
    data = {
    "keyphrase": "INCORRECTPASSWORDHERE",
    "name": "unit_test01",
    "ca_name": ca_name,
    "common_name": "google.com",
    "organisation_name": "Somehthing",
    "organisational_unit_name": "dasdasdas",
    "email": "sdasdasd",
    "locality": "dadasdasd",
    "state": "adsasda",
    "country": "US",
    "overwrite":True
    }
    r = requests.post(f"{API_URL}/create/certificate/{ca_id}/", headers=headers, json=data)

    reply = r.json()
    assert r.status_code != 200

def test_user_list_permissions():
    
    # should list all users because manager has *
    # previous tests have created users by this point
    # users without perms will only show themselves.
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/user/details/list/", headers=headers)
    reply = r.json()
    assert len(reply["result"]["users"]) > 1
    
    # now test a user without the perms
    user_token = get_auth_token("read", AUTHENTICATION_STORE["read"]["password"])
    headers = {"authorization":f"Bearer {user_token}"}
    r = requests.get(f"{API_URL}/user/details/list/", headers=headers)
    reply = r.json()
    assert len(reply["result"]["users"]) == 1

def test_token_expiry():
    
    data = {"username": "manager", "password":AUTHENTICATION_STORE["manager"]["password"]}
    r = requests.post(f"{API_URL}/user/login/?short=true", json=data) # adding short=true issues a token for 5 seconds
    reply = r.json()
    short_token = reply["token"]
    
    print("sleeping for expiry.")
    headers = {"authorization":f"Bearer {short_token}"}
    time.sleep(5.5)

    r = requests.get(f"{API_URL}/user/details/me/", headers=headers)
    reply = r.json()
    assert "Token expired" in reply["errors"]
    
   

#  -------------
# | TESTS END  |
#  -------------   

# clean up from hereon - do not run any full operational tests

def test_delete_cert():
    
    # create at least one cert before running this test
    headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
    r = requests.get(f"{API_URL}/list/certificates/", headers=headers)
    reply = r.json()
    
    len_pre = len(reply["result"])
    target_cert = reply["result"][0]
    
    cert_fp = os.path.join("/tmp", target_cert["parent_ca_sys_id"], "certs", target_cert["name"], f"{target_cert['name']}.crt")
    
    assert os.path.exists(cert_fp)
    
    
    # issue delete
    # 127.0.0.1:5001/delete/certificate/27ef5c47-1415-4666-91e2-1cf2049f3d63/nessus0gdgdfgdfgdffgfdgdfgd1123
    r = requests.get(f"{API_URL}/delete/certificate/{target_cert['parent_ca_sys_id']}/{target_cert['name']}", headers=headers)
    reply = r.json()
    assert r.status_code == 200
    
    # check not on disk
    assert not os.path.exists(cert_fp)

    # check one less    
    r = requests.get(f"{API_URL}/list/certificates/", headers=headers)
    reply = r.json()
    assert len(reply["result"]) == len_pre -1


def test_delete_ca():
    
    def get_all():    
        # create at least one cert before running this test
        headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}
        r = requests.get(f"{API_URL}/list/certauthority/", headers=headers)
        reply = r.json()
        ca_list = reply["result"]
        return ca_list
    
    all = get_all()
    pre_len = len(all)
    
    for idx, ca in enumerate(all):
        
        headers = {"authorization":f"Bearer {API_CURRENT_SESSION_TOKEN}"}

        ca_path = os.path.join("/tmp", ca["sys_id"])
        assert os.path.exists(ca_path)
        
        r = requests.get(f"{API_URL}/delete/certauthority/{ca['sys_id']}/", headers=headers)
        assert r.status_code == 200
        
        human_count = idx +1
        current_count = len(get_all())
        assert current_count == pre_len - human_count
    
    