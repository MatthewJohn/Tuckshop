#!/bin/bash

# Start the celert worker for Skype in the background
C_FORCE_ROOT=1 celery worker --concurrency 1 --app tuckshop.core.skype.skype_celery -b $RABBITMQ_URL -D

# Run unit tests
python ./scripts/start_tests.py

# Sync the database schema and perform migrations
python ./manage.py syncdb

# Start tuckshop server in foreground
python ./tuckshopaccountant.py > output.log
