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
else
    exec "$@"
fi