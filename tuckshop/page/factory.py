"""Provides factory functions for the page classes"""

from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound
from tuckshop.page.login import Login
from tuckshop.page.logout import Logout
from tuckshop.page.credit import Credit
from tuckshop.page.redirect import Redirect
from tuckshop.page.static_file import JS, CSS, Font, Favicon
from tuckshop.page.history.personal import Personal as PersonalHistory
from tuckshop.page.history.shared import Shared as SharedHistory
from tuckshop.page.history.stock import Stock as StockHistory
from tuckshop.page.history.unpaid_stock import UnpaidStock
from tuckshop.page.history.shared_accounts import SharedAccounts as SharedAccountsHistory
from tuckshop.page.stock import Stock
from tuckshop.page.admin.admin import Admin
from tuckshop.page.admin.permission import Permission
from tuckshop.page.float import Float
from tuckshop.page.item_image import ItemImage

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
            page_object = PersonalHistory(request_handler)
        elif name == 'stock-history':
            page_object = StockHistory(request_handler)
        elif  name == 'shared-history':
            page_object = SharedHistory(request_handler)
        elif name == 'unpaid-stock':
            page_object = UnpaidStock(request_handler)
        elif name == 'shared-account-history':
            page_object = SharedAccountsHistory(request_handler)
        elif name == 'stock':
            page_object = Stock(request_handler)
        elif name == 'admin':
            page_object = Admin(request_handler)
        elif name == 'permission':
            page_object = Permission(request_handler)
        elif name == 'float':
            page_object = Float(request_handler)
        elif name == 'favicon.ico':
            page_object = Favicon(request_handler)
        elif name == 'item-image':
            page_object = ItemImage(request_handler)
        else:
            page_object = NotFound(request_handler)

        if page_object.requiresLogin():
            # If page requires login, redirect to login page
            redirect_url = Login.getLoginUrl(request_handler)
            page_object = Redirect(redirect_url=redirect_url, request_handler=request_handler)
        elif page_object.requiresPermission():
            page_object = NotFound(request_handler)

        return page_object
