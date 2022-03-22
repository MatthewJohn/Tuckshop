#!/bin/bash

virtualenv -ppython2 venv
. venv/bin/activate

pip install django==1.8.7 dj-database-url SkPy celery==3.1.25 requests redis==2.10.5 raven enum34 python-ldap Pillow jinja2


docker run -p 0.0.0.0:15672:15672  -p 0.0.0.0:5672:5672 rabbitmq:3-management

docker run -p 0.0.0.0:6379:6379 redis

TUCKSHOP_DEVEL=True DJANGO_SETTINGS_MODULE=tuckshop.settings  C_FORCE_ROOT=1 celery worker --concurrency 1 --app tuckshop.core.celery_con.celery -I tuckshop.core.skype -I tuckshop.core.simulation -l info --purge --time-limit 30 -b localhost

TUCKSHOP_DEVEL=True python ./tuckshopaccountant.py


