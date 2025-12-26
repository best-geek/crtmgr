#!/bin/bash
set -e

echo "[i] Starting build $(date)"

echo "[i] Making persistent location for container"
mkdir -p persistent_api
echo "[✓] Persistent location created"



# copy python source code to API source
echo "[i] Copying Python source code"
cp python/*.py ct/api/python
cp python/config.conf ct/api/python
cp python/requirements.txt ct/api/python
echo "[✓] Copied Python files"

# build Vue app
echo "[i] Build Vue app"
cd vue/certmanager_ui
npm run build
cd ../../
echo "[✓] Built Vue app"

# copy build files to Apache front end
echo "[i] Copy Vue src files"
rm -rf ct/apache/src/*
cp -r vue/certmanager_ui/dist/* ct/apache/src/
cp vue/certmanager_ui/public/favicon.ico ct/apache/src
cp -r vue/certmanager_ui/public/icons ct/apache/src/icons
echo "[✓] Copied vue files"


# generate new Apache certs
echo "[i] Generate new apache certificates"
cd ct/apache/certs
./create-certs.sh 
cd ../../../
echo "[✓] Generated new front-end certs"



# start docker build
echo "[i] Starting Docker build"
docker compose build
echo "[✓] Complete Docker build"
