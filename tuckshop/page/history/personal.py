"""Contains class for history page"""
from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config

class Personal(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'Personal History'
    TEMPLATE = 'personal_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    URL = '/history'
    SUB_MENU_ORDER = 1
    SUB_MENU = HistoryBase
    MENU_ORDER = 2
    MENU_NAME = 'History'

    def getTransactionHistory(self):
        return self.getCurrentUserObject().getTransactionHistory()