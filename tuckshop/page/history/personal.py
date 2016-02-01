"""Contains class for history page"""
from math import ceil

from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config

class Personal(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'History'
    TEMPLATE = 'personal_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    URL = '/history'

    def getTransactionHistory(self):
        return self.getCurrentUserObject().getTransactionHistory()