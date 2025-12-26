import argparse
import logging
from sql import crtmgr_database
from hashlib import sha3_512
import secrets
import jwt
import datetime as dt
import toml
import json
import time
from functools import wraps
from flask import jsonify, g, request
from config import resolve_config_file


logging.basicConfig(format="[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s", datefmt="%m/%d/%Y_%I:%M:%S")
logging.root.setLevel(logging.DEBUG)

conf_file = resolve_config_file("app")
with open(conf_file, "r") as f:
    APP_CONFIG = toml.load(f)


def make_user_table():

    crtmgr_db = crtmgr_database(bypass_exists=True)

    EXPECTED_COLUMNS = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "username": "TEXT UNIQUE NOT NULL",
        "password_hash": "TEXT",
        "password_salt": "TEXT",
        "type": "TEXT NOT NULL",
        "created": "INT NOT NULL",
        "expires": "INT",
        "owner":"TEXT",
        "roles": "json",
    }

    # Step 1: Create table if not exists
    crtmgr_db.insert_query(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            type TEXT NOT NULL
        )
    """
    )

    # Step 2: Get current columns
    existing_cols = crtmgr_db.select_query_dict("PRAGMA table_info(users)")
    existing_col_names = [x["name"] for x in existing_cols]

    # Step 3: Add any missing columns
    for col_name, col_def in EXPECTED_COLUMNS.items():
        if col_name not in existing_col_names:
            logging.info(f"Adding missing column: {col_name}")
            crtmgr_db.insert_query(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")

def gen_salt():
    """Generates a cryptographically secure random salt for passwords"""
    logging.info("Generating salt for password")
    generated_salt = secrets.token_hex(20)
    logging.info("Generated salt successfully")
    return generated_salt

def secure_hash_password(plain_text="", pass_salt=""):
    """Securely generates a password with plain text and a salt"""

    if not plain_text:
        logging.error("No plaintext password supplied")
        return
    if not pass_salt:
        logging.error("No salt supplied")
        return

    if len(plain_text) < 8:
        logging.warning("Supplied plain text password less than 8 in len. Not secure.")

    # goes through and securely generates a hashed password

    # takes each char, multiplies by it's position and generates a hash
    # added that chars hash to a base hash which will get hashed later
    base_hash_str = ""
    for i in range(0, len(plain_text)):
        update_str = i * plain_text
        hashed_portion = sha3_512(update_str.encode("utf-8"))
        base_hash_str += hashed_portion.hexdigest()

    # generate final hash
    base_hash_str += pass_salt
    final_hash = sha3_512(base_hash_str.encode("utf-8"))
    final_hash_str = final_hash.hexdigest()

    return final_hash_str

def create_jwt(username, secret, alg, ttl=0):
    crtmgr_db = crtmgr_database(bypass_exists=True)
    user_record = crtmgr_db.select_query_dict(f"SELECT * FROM USERS WHERE username == '{username}'")
    user_record = user_record[0]
    
    if user_record.get("roles"):
        try:
            roles = json.loads(user_record["roles"])
        except:
            roles = []
            
    # if we have not filled out the owner field, let's assume that the user is requesting
    # token for themselves and not api.                
    owner = user_record.get("owner", None)
    if not owner:
        owner=username
    
    

    now = dt.datetime.now(dt.timezone.utc)
    
    # allow a ttl to be specified so we can create a JWT token
    if ttl == 0:
        ttl = APP_CONFIG.get("jwt", {}).get("ttl_seconds", 14400)
        

    payload = {
        "sub": str(username),
        "type": user_record.get("type", "unknown"),
        "iat": now,
        "nbf": now,
        "exp": now + dt.timedelta(seconds=ttl),
        "iss": "com.cert_manager.authentication",
        "aud": "com.cert_manager",
        "own": owner,
        "roles_at_iat": roles,
    }
    token = jwt.encode(payload, secret, algorithm=alg)
    logging.debug(f"JWT created for user: '{username}' with secret: '{secret}', alg: '{alg}'")
    
    return token

def decode_jwt(token, secret, alg): 
    
    return jwt.decode(
        token,
        secret,
        algorithms=[alg],
        audience="com.cert_manager",
        issuer="com.cert_manager.authentication",
        options={"require": ["exp", "iat", "nbf", "sub", "own"]},
    )

def get_bearer_token(request):
    authz = request.headers.get("Authorization", "")
    if authz.lower().startswith("bearer "):
        return authz.split(None, 1)[1].strip()
    # Fallbacks if you prefer (comment out if not needed):
    token = request.args.get("access_token") or request.cookies.get("access_token")
    return token

def get_src_ip(request):
    if request.headers.getlist("X-Forwarded-For"):
        # X-Forwarded-For may contain multiple IPs, take the first (client's IP)
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        # Fallback to the remote address directly from the request
        ip = request.remote_addr
    return ip


def get_user_agent(request):
    user_agent = request.headers.get("User-Agent")
    if not user_agent:
        user_agent = "Unknown"
    return user_agent

def auth_required(f):
    """
    Use on routes that require a valid Bearer token.
    Attaches g.username when valid.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        crtmgr_db = crtmgr_database(bypass_exists=True)
        resp = {"errors": []}
        secrets = APP_CONFIG["jwt"]["secret"]
        alg = APP_CONFIG["jwt"]["alg"]

        token = get_bearer_token(request)
        print(token)
        
        if not token:
            resp['errors'].append("'authorisation' header missing bearer token")
            return jsonify(resp), 403
        try:
            claims = decode_jwt(token, secrets, alg)
        except jwt.ExpiredSignatureError:
            resp['errors'].append("Token expired")
            return jsonify(resp), 403
        except jwt.InvalidTokenError as e:
            resp['errors'].append(f"Invalid token, {str(e)}")
            return jsonify(resp), 403

        # Ensure user still exists and is of the expected type
        username = claims["sub"]
        user_record = crtmgr_db.select_query_dict(
            f"SELECT * FROM users WHERE username = ?", (username,)
        )

        if not user_record:
            resp['errors'].append("User not found")
            return jsonify(resp), 401

        # Attach user to request context
        g.username = username
        
        # get other info
        g.src_ip = get_src_ip(request)
        g.user_agent = get_user_agent(request)
        
        return f(*args, **kwargs)
    return wrapper

def check_roles_jwt(request, allowed_roles=[]):
    resp = {"errors": []}
    secrets = APP_CONFIG["jwt"]["secret"]
    alg = APP_CONFIG["jwt"]["alg"]
    
    token = get_bearer_token(request)
    jwt=decode_jwt(token, secrets, alg)
    
    username = jwt["sub"]
    crtmgr_db = crtmgr_database(bypass_exists=True)
    user_record = crtmgr_db.select_query_dict(f"SELECT * FROM USERS WHERE username == '{username}'")
    if not user_record:
        return False
    user_record = user_record[0]
    
    user_roles = user_record.get("roles", '[]')
    user_roles = json.loads(user_roles)
    matched_roles = [r for r in user_roles if r in allowed_roles]
    print(matched_roles)
    
    return bool(matched_roles)

def user_login(username, password):
    crtmgr_db = crtmgr_database(bypass_exists=True)

    result = {"success": False, "data": ""}

    user_record = crtmgr_db.select_query_dict(f"SELECT * FROM USERS WHERE username == '{username}' AND type='user'")

    if not user_record:
        result["data"] = "Invalid user or password"
        return result
    user_record = user_record[0]

    hash_result = secure_hash_password(plain_text=password, pass_salt=user_record.get("password_salt", ""))
    if hash_result != user_record["password_hash"]:
        result["data"] = "Invalid user or password"
        return result

    secret = APP_CONFIG.get("jwt", {}).get("secret", "")
    if not secret:
        logging.error("The config file does not contain a 'secret' value under the JWT token. THIS IS INSECURE")

    alg = APP_CONFIG.get("jwt", {}).get("alg", "HS256")

    jwt = create_jwt(username=username, secret=secret, alg=alg)

    result["success"] = True
    result["data"] = jwt
    
    return result

def create_admin_user():
    crtmgr_db = crtmgr_database(bypass_exists=True)
    username = APP_CONFIG["auth"]["default_user"]
    
    q = f"DELETE FROM users WHERE username == '{username}'"
    crtmgr_db.insert_query(q)
 
    new_password = gen_salt()
    new_salt = gen_salt()
    roles = ["*"]
    now = int(time.time())
    password_hash = secure_hash_password(new_password, new_salt)

    q = f"INSERT INTO users (username, password_hash, type, created, password_salt, roles) VALUES ('{username}', '{password_hash}', 'user', '{now}', '{new_salt}', '{json.dumps(roles)}')"
    crtmgr_db.insert_query(q)
    
    logging.info(f"The password has been set to: {new_password}")
    return new_password

if __name__ == "__main__":
    make_user_table()  # make the user table incase it does not exist
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-admin", help="reset the 'manager' user password",action='store_true')
    args = parser.parse_args()
    
    if args.reset_admin:
        create_admin_user()
