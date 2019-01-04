#!/bin/bash -xe
python /app/manage.py migrate --noinput
python /app/manage.py migrate --database mi --noinput
python /app/manage.py init_es
python /app/manage.py collectstatic --noinput
sleep infinity
