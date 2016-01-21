"""Contains class for admin page"""

from tuckshop.app.models import User
from tuckshop.page.page_base import PageBase
from tuckshop.core.utils import getMoneyString
from tuckshop.core.tuckshop_exception import TuckshopException

class Admin(PageBase):

    NAME = 'Admin'
    TEMPLATE = 'admin'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = True

    def processPage(self):
        self.return_vars['users'] = User.objects.all()
        self.return_vars['unpaid_users'] = []
        for user in User.objects.all():
            if len(user.getUnpaidTransactions()):
                self.return_vars['unpaid_users'].append(user)

    def processPost(self):
        action = self.post_vars['action'] if 'action' in self.post_vars else None
        if action == 'pay_stock':
            if 'amount' not in self.post_vars:
                raise TuckshopException('Amount to pay must be specified and be a positive amount')
            try:
                float(self.post_vars['amount'])
            except:
                raise TuckshopException('Amount to pay must be specified and be a positive amount')

            amount = int(float(self.post_vars['amount']) * 100)
            user = User.objects.get(uid=self.post_vars['uid'])
            amount, semi_paid_transaction = user.payForStock(amount)
            if semi_paid_transaction:
                self.return_vars['warning'] = ('Not enough to fully pay transaction: %s' % semi_paid_transaction)
            elif amount:
                self.return_vars['warning'] = ('%s has been added as stock credit to %s' %
                                               (getMoneyString(amount, include_sign=False),
                                                self.post_vars['uid']))

        elif action == 'credit':
            if 'amount' not in self.post_vars or not int(self.post_vars['amount']):
                raise TuckshopException('Amount must be a positive integer')

            description = None if 'description' not in self.post_vars else self.post_vars['description']
            user = User.objects.get(uid=self.post_vars['uid'])
            user.addCredit(int(self.post_vars['amount']), description=description)
            self.return_vars['info'] = 'Added %s to %s' % (getMoneyString(self.post_vars['amount'], include_sign=False),
                                                           user.uid)
        elif action == 'debit':
            if 'amount' not in self.post_vars or not int(self.post_vars['amount']):
                raise TuckshopException('Amount must be a positive integer')

            description = None if 'description' not in self.post_vars else self.post_vars['description']
            user = User.objects.get(uid=self.post_vars['uid'])
            user.removeCredit(int(self.post_vars['amount']), description=description)
            self.return_vars['info'] = 'Removed %s from %s' % (getMoneyString(self.post_vars['amount'], include_sign=False),
                                                               user.uid)
