#!/bin/bash
set -e

echo "Start time: $(date)"

echo "Rsync files from source"
rsync -a --stats /code-source/ /api/

while getopts m:t: flag
do
    case "${flag}" in
        m) mode=${OPTARG};;
        t) type=${OPTARG};;
    esac
done

# check mode
if [ -z $mode ]
then
    echo "Mode not set. Use -m testing/prod"
    exit
fi

if [ -z $type ]
then
    echo "Type not set. Use -t api"
    exit
fi


# run any initial setup scripts. Take a basic config for app if not there
APP_CONF_FP=$(python3 /api/config.py --type="app" | tr -d '"')
echo "Resolved app config path to $APP_CONF_FP"
if [ ! -f $APP_CONF_FP ]
then
    cp /api/config.conf $APP_CONF_FP
    echo "Copied skeleton config"
fi

# script will setup db schema and config files
python3 /api/full_setup.py --full --container



echo "Start server with type ${type} in mode ${mode}"

# open debug version
if [ "${mode}" = "testing" ] && [ "${type}" = "api" ]; then
    echo "Starting Flask API server in testing mode"
    cd /api
    python3 api_server.py
fi

# open production version
if [ "${mode}" == "prod" ] && [ "${type}"=="api" ]; then
    echo "Starting gunicorn server in production mode"
    cd /api/
    gunicorn --bind 0.0.0.0:${RUN_PORT} api_server:app
fi

echo "WARNING! Server may not have been started or has been recently terminated"
echo "Sample command use: ./init.sh -m prod -t api"
exit% 
