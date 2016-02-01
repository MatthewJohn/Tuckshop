"""Contains class for history page"""
from tuckshop.page.history.history_base import HistoryBase
from tuckshop.core.config import Config
from tuckshop.core.permission import Permission
from tuckshop.app.models import Transaction


class SharedAccounts(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'Shared Accounts'
    TEMPLATE = 'shared_account_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.REVIEW_SHARED_ACCOUNTS
    URL = '/shared-account-history'
    SUB_MENU_ORDER = 3
    SUB_MENU = HistoryBase

    def getTransactionHistory(self):
        return Transaction.objects.filter(user__shared=True)
