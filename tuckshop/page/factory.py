"""Provides factory functions for the page classes"""

from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound
from tuckshop.page.login import Login
from tuckshop.page.logout import Logout
from tuckshop.page.credit import Credit
from tuckshop.page.redirect import Redirect
from tuckshop.page.static_file import JS, CSS, Font
from tuckshop.page.history import History
from tuckshop.page.stock_history import StockHistory
from tuckshop.page.stock import Stock
from tuckshop.page.admin import Admin

class Factory(object):
    """Factory class for obtaining page objects"""

    @staticmethod
    def getPageObject(request_handler):
        """Returns a page object for the current
           request, based on the URL path"""
        name = PageBase.getUrlBase(request_handler)
        page_object = None
        if name == 'credit' or name == '':
            page_object = Credit(request_handler)
        elif name == 'login':
            page_object = Login(request_handler)
        elif name == 'logout':
            page_object = Logout(request_handler)
        elif name == 'js':
            page_object = JS(request_handler)
        elif name == 'css':
            page_object = CSS(request_handler)
        elif name == 'font':
            page_object = Font(request_handler)
        elif name == 'history':
            page_object = History(request_handler)
        elif name == 'stock-history':
            page_object = StockHistory(request_handler)
        elif name == 'stock':
            page_object = Stock(request_handler)
        elif name == 'admin':
            page_object = Admin(request_handler)
        else:
            page_object = NotFound(request_handler)

        if page_object.requiresLogin():
            # If page requires login, redirect to login page
            redirect_url = Login.getLoginUrl(request_handler)
            page_object = Redirect(request_handler, redirect_url)
        elif page_object.requiresAdminAccess():
            page_object = NotFound(request_handler)

        return page_object
