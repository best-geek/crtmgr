#!/bin/bash
openssl req -x509 \
 -nodes -days 730 -newkey rsa:4096 \
 -keyout website.key \
 -out website.pem \
 -subj "/C=UK/ST=UK/L=London/CN=crtmgr.localhost/emailAddress=manager@localhost"
