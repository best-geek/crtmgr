from urllib import response
import flask
from io import BytesIO
from flask import send_file
from flask import jsonify
from flask import request
from flask_cors import CORS
import logging
from logging import handlers
import zipfile


from api_server_helpers import *

logger = logging.getLogger("")
formatter = logging.Formatter("[%(filename)s:%(lineno)d] [fun:%(funcName)s] %(asctime)s [%(levelname)s] %(message)s")
logging.basicConfig(
                    format=formatter, 
                    datefmt="%m/%d/%Y_%I:%M:%S"
                    )
logging_fh = handler = handlers.RotatingFileHandler(
    "api_server.log", maxBytes=(1048576*5), backupCount=7
)
logging.root.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(logging_fh)


# remove stream system logs, because junks up when actively streaming
class NoHealthLogFilter(logging.Filter):
    def filter(self, record):
        return '/system/logs/' not in record.getMessage()
logging.getLogger('werkzeug').addFilter(NoHealthLogFilter())


# configure flask
app = flask.Flask(__name__)
LISTEN_PORT = 5001


@app.route("/", methods=["POST", "GET"])
def root():
    result = {"ping":"pong", "info":"crtmgr"}
    return jsonify(result)


@app.route("/create/certauthority/", methods=["POST"])
@auth_required
def create_certauthority():
    passed_role_check = check_roles_jwt(request, ["*", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = create_certauthority_helper(request)
    return jsonify(result), code


@app.route("/delete/certauthority/<ca_id>/", methods=["GET"])
@auth_required
def delete_certauthority(ca_id):
    passed_role_check = check_roles_jwt(request, ["*", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = delete_certauthority_helper(ca_id)
    return jsonify(result), code


@app.route("/download/certauthority/<ca_id>/", methods=["GET"])
@auth_required
def download_certauthority(ca_id):
    buffer = request.args.get("buffer", "")
    if buffer == "true":
        buffer = True
    else:
        buffer = False 
    
    passed_role_check = check_roles_jwt(request, ["*", "read", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = download_certauthority_helper(ca_id)
    if buffer:
        logging.debug("Buffering request")
        buffer = BytesIO()
        result = result.get("result", {}).get("cert", "")
        buffer.write(result.encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer, download_name=f"{ca_id}.pem",mimetype='text', as_attachment=True)
    if not buffer:
        return jsonify(result), code

@app.route("/list/certauthority/", methods=["GET"])
@auth_required
def list_certauthority():
    passed_role_check = check_roles_jwt(request, ["*", "read"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = list_certauthority_helper()
    return jsonify(result), code

@app.route("/list/certificates/", methods=["GET"])
@auth_required
def list_certificates():
    passed_role_check = check_roles_jwt(request, ["*", "read"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = list_certificates_helper()
    return jsonify(result), code

@app.route("/delete/certificate/<ca_id>/<cert_name>/", methods=["GET"])
@auth_required
def delete_certificate(ca_id, cert_name):
    passed_role_check = check_roles_jwt(request, ["*", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    
    result, code = delete_certificate_helper(ca_id, cert_name)
    return jsonify(result), code


@app.route("/create/certificate/<ca_id>/", methods=["POST"])
@auth_required
def create_certificate(ca_id):
    passed_role_check = check_roles_jwt(request, ["*", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    result, code = create_certificate_helper(request, ca_id)
    return jsonify(result), code

@app.route("/download/certificate/<ca_id>/<cert_name>/", methods=["GET"])
@auth_required
def download_certificate(ca_id, cert_name):
    buffer = request.args.get("buffer", "")
    if buffer == "true":
        buffer = True
    else:
        buffer = False 
        
        
    passed_role_check = check_roles_jwt(request, ["*", "read", "write"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    result, code = download_certificate_helper(ca_id, cert_name)
    if buffer:
        logging.debug("Buffering request")
        cert = result.get("result", {}).get("cert", "")
        key = result.get("result", {}).get("key", "")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(f"{cert_name}.pem", cert)
            zipf.writestr(f"{cert_name}.key", key)                
        zip_buffer.seek(0)
        
        return send_file(zip_buffer, download_name=f"{ca_id}_{cert_name}.zip", as_attachment=True)
    if not buffer:
        return jsonify(result), code

@app.route("/user/login/", methods=["POST"])
def user_login():
    result, code = user_login_helper(request)
    return jsonify(result), code

@app.route("/user/resetpassword/<for_user>/", methods=["POST"])
@auth_required
def user_resetpassword(for_user):
    # g.username is passed from auth_required decorator
    if g.username != for_user:            
        passed_role_check = check_roles_jwt(request, ["*", "manage_users"])
        if not passed_role_check:
            return jsonify({"errors":"invalid permissions"})
    result, code = user_resetpassword_helper(request, for_user)
    return jsonify(result), code
    
@app.route("/user/details/list/", methods=["GET"])
@auth_required
def user_details_list():
    # g.username is passed from auth_required decorator
    for_user = g.username
    if check_roles_jwt(request, ["*", "manage_users"]):            
        for_user = "*" # if we have permissions, set everybody 
        logging.info("querying all users")       
    result, code = user_details_helper(for_user)
    return jsonify(result), code

@app.route("/user/create/", methods=["POST"])
@auth_required
def user_create():
    # g.username is passed from auth_required decorator
    for_user = g.username
    passed_role_check = check_roles_jwt(request, ["*", "manage_users"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
    result, code =user_create_helper(request, for_user)

    return jsonify(result), code



@app.route("/user/details/me/", methods=["GET"])
@auth_required
def user_details_me():
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code = user_details_helper(for_user)
    return jsonify(result), code


@app.route("/user/profile/<for_user>/update/", methods=["POST"])
@auth_required
def user_profile_update(for_user):
    if g.username != for_user:            
        passed_role_check = check_roles_jwt(request, ["*", "manage_users"])
        if not passed_role_check:
            return jsonify({"errors":"invalid permissions"})
    # g.username is passed from auth_required decorator
    result, code = user_profile_update_helper(request, for_user, g.username)
    return jsonify(result), code


@app.route("/user/profile/<for_user>/delete/", methods=["POST"])
@auth_required
def user_profile_delete(for_user):
    if g.username != for_user:            
        passed_role_check = check_roles_jwt(request, ["*", "manage_users"])
        if not passed_role_check:
            return jsonify({"errors":"invalid permissions"})
    # g.username is passed from auth_required decorator
    result, code = user_profile_delete_helper(for_user, g.username)
    return jsonify(result), code


@app.route("/user/apikeys/create/", methods=["POST"])
@auth_required
def user_apikeys_create():
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code =user_apikeys_create_helper(request, for_user)
    return jsonify(result), code

@app.route("/user/apikeys/list/", methods=["GET"])
@auth_required
def user_apikeys_list():
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code =user_apikeys_list_helper(for_user)
    return jsonify(result), code

@app.route("/user/apikeys/delete/<keyid>/", methods=["GET"])
@auth_required
def user_apikeys_delete_keyid(keyid):
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code =user_apikeys_delete_keyid_helper(for_user, keyid)
    return jsonify(result), code


@app.route("/system/logs/", methods=["GET"])
@auth_required
def system_logs():
    stream = request.args.get('stream', 'no')
    stream_logs = (stream == "true")
    
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code =system_logs_helper(stream_logs)
    return jsonify(result), code



@app.route("/system/logs/syslog/", methods=["POST"])
@auth_required
def system_logs_syslog():

          
    passed_role_check = check_roles_jwt(request, ["*", "system_admin"])
    if not passed_role_check:
        return jsonify({"errors":"invalid permissions"})
            
    # g.username is passed from auth_required decorator
    for_user = g.username            
    result, code =system_logs_syslog_helper(request)
    return jsonify(result), code


# so we can run as a module
if __name__ == "__main__":
    print("Starting API")
    CORS(app)
    app.run(host="0.0.0.0", port=int(LISTEN_PORT), debug=False)