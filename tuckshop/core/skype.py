
from skpy import Skype as SkypeAPI
import time
import os
from celery import Celery

from tuckshop.core.config import Config

redis_url = os.environ['REDIS_URL'] if 'REDIS_URL' in os.environ else 'redis://localhost'
skype_celery = Celery('skype', broker='pyamqp://guest@localhost//', backend=redis_url)


class Skype(object):

    SKYPE_CONNECTION = None
    SKYPE_OBJECT = None

    @staticmethod
    def get_object():
        if Skype.SKYPE_OBJECT is None:
            Skype.SKYPE_OBJECT = Skype()
        return Skype.SKYPE_OBJECT

    def get_connection(self):
        credentials = Config.SKYPE_CREDENTIALS()
        if credentials is None:
            raise Exception('No skype credentials available')

        if Skype.SKYPE_CONNECTION is None:
            try:
                Skype.SKYPE_CONNECTION = SkypeAPI(credentials[0], credentials[1])
            except:
                time.sleep(3)
                Skype.SKYPE_CONNECTION = SkypeAPI(credentials[0], credentials[1])
        return Skype.SKYPE_CONNECTION

    @skype_celery.task(bind=True)
    def send_message(self, user_id, message):
        print 'test'
        try:
            if Skype.get_object().contact_exists(user_id):
                user = Skype.get_object().get_connection().contacts.user(user_id)
                chat = user.chat
                chat.sendMsg(message)
        except:
            Skype.SKYPE_CONNECTION = None
            if Skype.get_object().get_connection().contact_exists(user_id):
                user = Skype.get_object().get_connection().contacts.user(user_id)
                chat = user.chat
                chat.sendMsg(message)

    def contact_exists(self, user_id):
        for request in self.get_connection().contacts.requests():
            if request.user.id == user_id:
                request.accept()
                return True

        for contact in self.get_connection().contacts:
            if contact.id == user_id:
                return True

        return False