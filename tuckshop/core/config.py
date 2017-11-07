from os import environ

class Config(object):

    @staticmethod
    def str2bool(v):
      return v.lower() in ("yes", "y", "true", "t", "1")

    @staticmethod
    def SHOW_OUT_OF_STOCK_ITEMS():
        return True if 'SHOW_OUT_OF_STOCK_ITEMS' not in environ else Config.str2bool(environ['SHOW_OUT_OF_STOCK_ITEMS'])

    @staticmethod
    def TRANSACTION_PAGE_SIZE():
        return 10 if 'TRANSACTION_PAGE_SIZE' not in environ else int(environ['TRANSACTION_PAGE_SIZE'])

    @staticmethod
    def TOTAL_PAGE_DISPLAY():
        return 7 if 'TOTAL_PAGE_DISPLAY' not in environ else int(environ['TOTAL_PAGE_DISPLAY'])


    @staticmethod
    def APP_NAME():
        return 'ITDev Tuck Shop' if 'APP_NAME' not in environ else environ['APP_NAME']

    @staticmethod
    def ENABLE_CUSTOM_PAYMENT():
        return True if 'ENABLE_CUSTOM_PAYMENT' not in environ else Config.str2bool(environ['ENABLE_CUSTOM_PAYMENT'])

    @staticmethod
    def LDAP_SERVER():
        return 'localhost' if 'LDAP_SERVER' not in environ else environ['LDAP_SERVER']

    @staticmethod
    def LDAP_USER_BASE():
        return None if 'LDAP_USER_BASE' not in environ else environ['LDAP_USER_BASE']

    @staticmethod
    def SKYPE_CREDENTIALS():
        return (environ['SKYPE_USERNAME'], environ['SKYPE_PASS']) if 'SKYPE_USERNAME' in environ and 'SKYPE_PASS' in environ else None

    @staticmethod
    def DEVEL():
        return True if 'TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL'] else False
