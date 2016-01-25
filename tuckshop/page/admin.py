"""Contains class for admin page"""

from tuckshop.app.models import User
from tuckshop.page.page_base import PageBase, VariableVerificationTypes
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
        action = self.getPostVariable(name='action', possible_values=['pay_stock', 'credit', 'debit'])
        uid = self.getPostVariable(name='uid', var_type=str)
        if action == 'pay_stock':
            amount = self.getPostVariable(name='amount', special=[VariableVerificationTypes.FLOAT_MONEY,
                                                                  VariableVerificationTypes.POSITIVE],
                                          message='Amount to pay must be specified and be a valid positive amount')
            # Convert amout from pounds to pence
            amount = int(amount * 100)
            user = User.objects.get(uid=uid)
            amount, semi_paid_transaction = user.payForStock(author_user=self.getCurrentUserObject(),
                                                             amount=amount)
            if semi_paid_transaction:
                self.return_vars['warning'] = ('Not enough to fully pay transaction: %s' % semi_paid_transaction)
            elif amount:
                self.return_vars['warning'] = ('%s has been added as stock credit to %s' %
                                               (getMoneyString(amount, include_sign=False), uid))

        elif action == 'credit':
            amount = self.getPostVariable(name='amount', special=[VariableVerificationTypes.POSITIVE], var_type=int,
                                          message="Amount must be a positive amount in pence")
            description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True)

            user = User.objects.get(uid=uid)
            user.addCredit(amount, description=description)
            self.return_vars['info'] = 'Added %s to %s' % (getMoneyString(amount, include_sign=False),
                                                           user.uid)
        elif action == 'debit':
            amount = self.getPostVariable(name='amount', special=[VariableVerificationTypes.POSITIVE], var_type=int,
                                          message="Amount must be a positive amount in pence")
            description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True)

            user = User.objects.get(uid=uid)
            user.removeCredit(amount, description=description)
            self.return_vars['info'] = 'Removed %s from %s' % (getMoneyString(amount, include_sign=False),
                                                               user.uid)
