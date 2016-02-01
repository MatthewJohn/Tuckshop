"""Contains class for history page"""
from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config

class Shared(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'Purchases on Shared Accounts'
    TEMPLATE = 'shared_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    URL = '/shared-history'

    def getTransactionHistory(self):
        return self.getCurrentUserObject().getTransactionHistory(author=True)
