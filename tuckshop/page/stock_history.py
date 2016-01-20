"""Contains class for stock history page"""
from math import ceil

from tuckshop.page.page_base import PageBase
from tuckshop.core.config import TRANSACTION_PAGE_SIZE

class StockHistory(PageBase):
    """Class for displaying a history page"""

    NAME = 'Stock History'
    TEMPLATE = 'stock_history'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        """Obtains required variables for stock history page"""
        stock_payments = self.getCurrentUserObject().getStockPayments()
        url_parts = StockHistory.getUrlParts(self.request_handler)
        self.return_vars['page_data'] = []
        if len(stock_payments) > TRANSACTION_PAGE_SIZE:
            page_number = int(url_parts[2]) if len(url_parts) == 3 else 1
            total_pages = int(ceil((len(stock_payments) - 1) / TRANSACTION_PAGE_SIZE)) + 1
            self.return_vars['page_data'] = self.getPaginationData(page_number,
                                                                   total_pages,
                                                                   '/stock-history/%s')
            array_start = (page_number - 1) * TRANSACTION_PAGE_SIZE
            array_end = page_number * TRANSACTION_PAGE_SIZE
            stock_payments = stock_payments[array_start:array_end]

        self.return_vars['payements'] = stock_payments

    def processPost(self):
        """Defines post method, but not required, as stock history
           page has no POST methods"""
        pass
