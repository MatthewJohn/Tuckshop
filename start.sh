#!/bin/bash

# Start the celert worker for Skype in the background
DJANGO_SETTINGS_MODULE=tuckshop.settings  C_FORCE_ROOT=1 celery worker --concurrency 1 --app tuckshop.core.celery_con.celery -I tuckshop.core.skype -I tuckshop.core.simulation -l info --purge --time-limit 30 -b $RABBITMQ_URL -D

# Run unit tests
python ./scripts/start_tests.py

# Sync the database schema and perform migrations
python ./manage.py syncdb

# Start tuckshop server in foreground
python ./tuckshopaccountant.py
