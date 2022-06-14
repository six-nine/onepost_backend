#!/bin/sh

python3 manage.py collectstatic --noinput --clear 
python3 manage.py makemigrations posts
python3 manage.py migrate

exec "$@"
