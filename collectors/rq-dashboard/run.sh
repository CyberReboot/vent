#! /bin/bash

set -x

if [[ -z "$REMOTE_REDIS_HOST" ]]; then
    echo "NEED TO SET REMOTE_REDIS_HOST env var. If redis on host machine, set to public ip for host machine"
    exit 11
fi

if [[ -z "$REMOTE_REDIS_PORT" ]]; then
    export REMOTE_REDIS_PORT="6379"
fi

if [[ -z "$REMOTE_REDIS_PSWD" ]]; then  #should i fail if not set?
    echo "REMOTE_REDIS_PSWD not set. Please SET"
    export REMOTE_REDIS_PSWD=""
fi

if [[ -z "$DASH_PREFIX" ]]; then  #should i fail if not set?
    export DASH_PREFIX="/rq"
fi

export RQ_DASHBOARD_SETTINGS="/rq-dash-settings.py"

echo "REMOTE_REDIS_HOST=${REMOTE_REDIS_HOST} REMOTE_REDIS_PORT=${REMOTE_REDIS_PORT}"

rq-dashboard
