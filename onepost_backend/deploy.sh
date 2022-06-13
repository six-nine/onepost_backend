#!/bin/bash

docker-compose -f docker-compose.deploy.yaml up -d --build
docker-compose -f docker-compose.deploy.yaml exec backend python manage.py migrate --noinput
docker-compose -f docker-compose.deploy.yaml exec backend python manage.py collectstatic --no-input --clear
