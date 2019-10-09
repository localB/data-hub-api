#!/usr/bin/env bash

# Start-up script for the web process, primarily for GOV.UK PaaS (see the Procfile)

set  -xe

./manage.py distributed_migrate --noinput
./manage.py init_es
gunicorn config.wsgi --config config/gunicorn.py
