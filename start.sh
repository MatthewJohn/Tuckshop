#!/bin/bash

# Start the rabbitmq server
service rabbitmq-server start

# Start the celert worker for Skype in the background
celery worker --concurrency 1 --app tuckshop.core.skype.skype_celery -b 'pyamqp://guest@localhost//' -D

# Run unit tests
python ./scripts/start_tests.py

# Sync the database schema and perform migrations
python ./manage.py syncdb

# Start tuckshop server in foreground
python ./tuckshopaccountant.py
