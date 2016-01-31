"""Contains class for stock history page"""
from math import ceil

from tuckshop.page.page_base import PageBase
from tuckshop.core.config import Config

class StockHistory(PageBase):
    """Class for displaying a history page"""

    NAME = 'Stock History'
    TEMPLATE = 'stock_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None

    def processPage(self):
        """Obtains required variables for stock history page"""
        stock_payment_transactions = self.getCurrentUserObject().getStockPaymentTransactions()
        url_parts = StockHistory.getUrlParts(self.request_handler)
        self.return_vars['page_data'] = []
        if len(stock_payment_transactions) > Config.TRANSACTION_PAGE_SIZE():
            page_number = int(url_parts[2]) if len(url_parts) == 3 else 1
            total_pages = int(ceil((len(stock_payment_transactions) - 1) / Config.TRANSACTION_PAGE_SIZE())) + 1
            self.return_vars['page_data'] = self.getPaginationData(page_number,
                                                                   total_pages,
                                                                   '/stock-history/%s')
            array_start = (page_number - 1) * Config.TRANSACTION_PAGE_SIZE()
            array_end = page_number * Config.TRANSACTION_PAGE_SIZE()
            stock_payment_transactions = stock_payment_transactions[array_start:array_end]

        self.return_vars['stock_payment_transactions'] = stock_payment_transactions

    def processPost(self):
        """Defines post method, but not required, as stock history
           page has no POST methods"""
        pass
