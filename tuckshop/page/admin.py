"""Contains class for admin page"""

from tuckshop.app.models import User
from tuckshop.page.page_base import PageBase
from tuckshop.core.utils import getMoneyString

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
            if 'amount' not in self.post_vars or not float(self.post_vars['amount']):
                self.return_vars['error'] = 'Amount to pay must be specified and be a positive amount'
                return
            amount = int(float(self.post_vars['amount']) * 100)
            user = User.objects.get(uid=self.post_vars['uid'])
            amount, semi_paid_transaction = user.payForStock(amount)
            if semi_paid_transaction:
                self.return_vars['warning'] = ('Not enough to fully pay transaction: '
                                               '%s (%s paid)' % (semi_paid_transaction,
                                                                 getMoneyString(amount,
                                                                                include_sign=False)))
            elif amount:
                self.return_vars['warning'] = ('%s left after paying for all transactions' %
                                               getMoneyString(amount, include_sign=False))

        elif action == 'credit':
            if 'amount' not in self.post_vars or not int(self.post_vars['amount']):
                self.return_vars['error'] = 'Amount must be a positive integer'
                return
            description = None if 'description' not in self.post_vars else self.post_vars['description']
            user = User.objects.get(uid=self.post_vars['uid'])
            user.addCredit(int(self.post_vars['amount']), description=description)
            self.return_vars['info'] = 'Added %s to %s' % (getMoneyString(self.post_vars['amount'], include_sign=False),
                                                           user.uid)
        elif action == 'debit':
            if 'amount' not in self.post_vars or not int(self.post_vars['amount']):
                self.return_vars['error'] = 'Amount must be a positive integer'
                return
            description = None if 'description' not in self.post_vars else self.post_vars['description']
            user = User.objects.get(uid=self.post_vars['uid'])
            user.removeCredit(int(self.post_vars['amount']), description=description)
            self.return_vars['info'] = 'Removed %s from %s' % (getMoneyString(self.post_vars['amount'], include_sign=False),
                                                               user.uid)
