#!/bin/bash

set -eu

if [ "$1" == "dbinit" ]; then
    poetry run cli dbinit
    poetry run alembic upgrade head
elif [ "$1" == 'api' ]; then
    poetry run python ./web/api.py
elif [ "$1" == "celery-beat" ]; then
    poetry run celery -A celery_app beat --loglevel=info
elif [ "$1" == "celery-worker" ]; then
    poetry run celery -A celery_app worker --loglevel=info
elif [ "$1" == "load-data-worker" ]; then
    poetry run celery -A celery_app worker -Q load_data_from_source_queue --loglevel=INFO -n worker2@%h
else
    exec "$@"
fi