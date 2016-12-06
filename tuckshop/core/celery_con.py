from celery import Celery
import os

JOBS = {}

redis_url = os.environ['REDIS_URL'] if 'REDIS_URL' in os.environ else 'redis://localhost'
broker_url = os.environ['RABBITMQ_URL'] if 'RABBITMQ_URL' in os.environ else 'pyamqp://guest@localhost//'
celery = Celery('skype', broker=broker_url, backend=redis_url)