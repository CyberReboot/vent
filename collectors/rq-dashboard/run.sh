#! /bin/bash

set -x

if [[ -z "$REDIS_HOST" ]]; then
    echo "NEED TO SET REDIS_HOST env var. If redis on host machine, set to public ip for host machine"
    exit 11
fi
if [[ -z "$REDIS_PORT" ]]; then
    export REDIS_PORT="6379"
fi
if [[ -z "$REDIS_PSWD" ]]; then  #should i fail if not set?
    echo "REDIS_PSWD not set. Please SET"
    export REDIS_PSWD=""
fi

if [[ -z "$DASH_PREFIX" ]]; then  #should i fail if not set?
    export DASH_PREFIX="/rq"
fi

export RQ_DASHBOARD_SETTINGS="/rq-dash-settings.py"

echo "REDIS_HOST=${REDIS_HOST} REDIS_PORT=${REDIS_PORT}"

rq-dashboard
