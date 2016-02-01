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

    def getHistoryMenu(self):
        from tuckshop.page.history.personal import Personal
        from tuckshop.page.history.shared import Shared
        from tuckshop.page.history.stock import Stock
        from tuckshop.page.history.shared_accounts import SharedAccounts
        rows = []
        template = """<ul class="nav nav-tabs">%s</ul>"""
        row_template = """<li role="presentation"%s><a href="%s">%s</a></li>"""
        for page_class in [Personal, Shared, Stock, SharedAccounts]:
            page_object = page_class(self.request_handler)
            if not page_object.requiresPermission():
                is_active = ' class="active"' if (self.__class__.__name__ == page_class.__name__) else ''
                rows.append(row_template % (is_active, page_object.URL, page_object.NAME))

        return template % ''.join(rows)

    def processPage(self):
        """Obtains required variables for history page"""
        transaction_history = self.getTransactionHistory()
        url_parts = HistoryBase.getUrlParts(self.request_handler)
        self.return_vars['page_data'] = []
        if len(transaction_history) > Config.TRANSACTION_PAGE_SIZE():
            # Attempt to retrieve page number from URL, default to 1
            page_number = 1
            if len(url_parts) == 3:
                try:
                    page_number = int(url_parts[2])
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
