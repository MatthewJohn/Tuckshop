"""Contains class for stock history page"""
from math import ceil

from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config

class Stock(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'Stock History'
    TEMPLATE = 'stock_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    URL = '/stock-history'

    def getTransactionHistory(self):
        return self.getCurrentUserObject().getStockPaymentTransactions()
