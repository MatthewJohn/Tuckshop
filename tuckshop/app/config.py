from os import environ

def str2bool(v):
  return v.lower() in ("yes", "y", "true", "t", "1")

LDAP_SERVER = 'localhost' if 'LDAP_SERVER' not in environ else environ['LDAP_SERVER']
SHOW_OUT_OF_STOCK_ITEMS = True if 'SHOW_OUT_OF_STOCK_ITEMS' not in environ else str2bool(environ['SHOW_OUT_OF_STOCK_ITEMS'])
TRANSACTION_PAGE_SIZE = 10 if 'TRANSACTION_PAGE_SIZE' not in environ else int(environ['TRANSACTION_PAGE_SIZE'])
TOTAL_PAGE_DISPLAY = 7 if 'TOTAL_PAGE_DISPLAY' not in environ else int(environ['TOTAL_PAGE_DISPLAY'])
APP_NAME = 'ITDev Tuck Shop' if 'APP_NAME' not in environ else environ['APP_NAME']
ENABLE_CUSTOM_PAYMENT = True if 'ENABLE_CUSTOM_PAYMENT' not in environ else str2bool(environ['ENABLE_CUSTOM_PAYMENT'])
