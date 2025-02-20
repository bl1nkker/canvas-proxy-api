#!/bin/bash

docker compose --project-name canvas-proxy-local \
               --file project/docker-compose.yml \
               down