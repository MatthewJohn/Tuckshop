
from skpy import Skype as SkypeAPI
import time

from tuckshop.core.config import Config

class Skype(object):

    SKYPE_CONNECTION = None

    @staticmethod
    def get_connection():
        credentials = Config.SKYPE_CREDENTIALS()
        if credentials is None:
            raise Exception('No skype credentials available')

        if Skype.SKYPE_CONNECTION is None:
            try:
                Skype.SKYPE_CONNECTION = SkypeAPI(credentials[0], credentials[1])
            except:
                time.sleep(3)
                Skype.SKYPE_CONNECTION = SkypeAPI(credentials[0], credentials[1])
        Skype.SKYPE_CONNECTION.setPresence()
        return Skype.SKYPE_CONNECTION


    @staticmethod
    def send_message(user_id, message):
        if Skype.contact_exists(user_id):
            user = Skype.get_connection().contacts.user(user_id)
            chat = user.chat
            chat.setTyping(active=True)
            chat.sendMsg(message)
            chat.setTyping(active=False)

    @staticmethod
    def contact_exists(user_id):
        for request in Skype.get_connection().contacts.requests():
            if request.user.id == user_id:
                request.accept()
                return True

        for contact in Skype.get_connection().contacts:
            if contact.id == user_id:
                return True

        return False