"""Contains class for history page"""
from tuckshop.page.history.history_base import HistoryBase
from tuckshop.page.admin.admin_base import AdminBase
from tuckshop.core.permission import Permission
from tuckshop.app.models import User as UserModel
from tuckshop.core.tuckshop_exception import TuckshopException

class User(HistoryBase):
    """Class for displaying a history page"""

    NAME = 'User History'
    TEMPLATE = 'user_history'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.ADMIN
    URL = '/user-history'
    SUB_MENU_ORDER = 6
    SUB_MENU = HistoryBase

    def getTransactionHistory(self):
        if len(User.getUrlParts(self.request_handler)) == 3:
            uid = User.getUrlParts(self.request_handler)[2]
            users = UserModel.objects.filter(uid=uid)
            if not len(users):
                raise TuckshopException('User %s does not exist' % uid)
            user = users[0]
            transactions = user.getTransactionHistory()
        else:
            user = None
            transactions = []

        self.return_vars['users'] = UserModel.objects.all()
        self.return_vars['user'] = user
        return transactions