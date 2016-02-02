"""Contains class for history page"""
from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config

class UnpaidStock(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'Unpaid Stock'
    TEMPLATE = 'unpaid_stock'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    URL = '/unpaid-stock'
    SUB_MENU_ORDER = 5
    SUB_MENU = HistoryBase

    def getTransactionHistory(self):
        return sorted(self.getCurrentUserObject().getUnpaidTransactions(), key=lambda x: x.timestamp, reverse=True)