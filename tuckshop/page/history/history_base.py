"""Contains class for history page"""
from math import ceil

from tuckshop.page.page_base import PageBase
from tuckshop.core.config import Config

class HistoryBase(PageBase):
    """Class for displaying a history page"""

    REQUIRES_AUTHENTICATION = True
    PERMISSION = None

    def getTransactionHistory(self):
        """Returns the transaction values to be displayed in the history page"""
        raise NotImplementedError

    @property
    def pagination_itx(self):
        """Pagination URL parts itx"""
        return 2

    def processPage(self):
        """Obtains required variables for history page"""
        transaction_history = self.getTransactionHistory()
        url_parts = HistoryBase.getUrlParts(self.request_handler)
        self.return_vars['page_data'] = []
        if len(transaction_history) > Config.TRANSACTION_PAGE_SIZE():
            # Attempt to retrieve page number from URL, default to 1
            page_number = 1
            if len(url_parts) == (self.pagination_itx + 1):
                try:
                    page_number = int(url_parts[self.pagination_itx])
                except ValueError:
                    pass

            total_pages = int(ceil((len(transaction_history) - 1) / Config.TRANSACTION_PAGE_SIZE())) + 1
            self.return_vars['page_data'] = self.getPaginationData(page_number, total_pages,
                                                                   '%s/%%s' % self.URL)
            array_start = (page_number - 1) * Config.TRANSACTION_PAGE_SIZE()
            array_end = page_number * Config.TRANSACTION_PAGE_SIZE()
            transaction_history = transaction_history[array_start:array_end]
        self.return_vars['transaction_history'] = transaction_history

    def processPost(self):
        """Defines post method, but not required, as history
           page has no POST methods"""
        pass
