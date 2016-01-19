"""Contains class for history page"""
from math import ceil

from tuckshop.page.page_base import PageBase
from tuckshop.core.config import TRANSACTION_PAGE_SIZE

class History(PageBase):
    """Class for displaying a history page"""

    NAME = 'History'
    TEMPLATE = 'history'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        """Obtains required variables for history page"""
        transaction_history = self.getCurrentUserObject().getTransactionHistory()
        url_parts = History.getUrlParts(self.request_handler)
        self.return_vars['page_data'] = []
        if len(transaction_history) > TRANSACTION_PAGE_SIZE:
            page_number = int(url_parts[2]) if len(url_parts) == 3 else 1
            total_pages = int(ceil((len(transaction_history) - 1) / TRANSACTION_PAGE_SIZE)) + 1
            self.return_vars['page_data'] = self.getPaginationData(page_number, total_pages,
                                                                   '/history/%s')
            array_start = (page_number - 1) * TRANSACTION_PAGE_SIZE
            array_end = page_number * TRANSACTION_PAGE_SIZE
            transaction_history = transaction_history[array_start:array_end]
        self.return_vars['transaction_history'] = transaction_history

    def processPost(self):
        """Defines post method, but not required, as history
           page has no POST methods"""
        pass
