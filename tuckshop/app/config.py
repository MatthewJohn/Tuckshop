from os import environ

LDAP_SERVER = 'localhost' if 'LDAP_SERVER' not in environ else environ['LDAP_SERVER']
SHOW_OUT_OF_STOCK_ITEMS = True if 'SHOW_OUT_OF_STOCK_ITEMS' not in environ else environ['SHOW_OUT_OF_STOCK_ITEMS']
TRANSACTION_PAGE_SIZE = 10 if 'TRANSACTION_PAGE_SIZE' not in environ else environ['TRANSACTION_PAGE_SIZE']
TOTAL_PAGE_DISPLAY = 7 if 'TOTAL_PAGE_DISPLAY' not in environ else environ['TOTAL_PAGE_DISPLAY']
APP_NAME = 'ITDev Tuck Shop' if 'APP_NAME' not in environ else environ['APP_NAME']