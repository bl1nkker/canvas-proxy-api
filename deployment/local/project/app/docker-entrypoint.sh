#!/bin/bash

set -eu

if [ "$1" == "dbinit" ]; then
    poetry run cli dbinit
    poetry run alembic upgrade head
elif [ "$1" == 'api' ]; then
    poetry run python ./web/api.py
else
    exec "$@"
fi