"""Contains class for admin page"""

from tuckshop.app.models import User
from tuckshop.page.page_base import VariableVerificationTypes
from tuckshop.page.admin.admin_base import AdminBase
from tuckshop.core.utils import getMoneyString
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.permission import Permission

class Admin(AdminBase):

    NAME = 'Admin'
    TEMPLATE = 'admin'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.ADMIN
    SUB_MENU_ORDER = 1
    MENU_ORDER = 5
    SUB_MENU = AdminBase
    URL = '/admin'

    def processPage(self):
        self.return_vars['users'] = User.objects.all().order_by('uid')
        self.return_vars['unpaid_users'] = []
        for user in User.objects.all().order_by('uid'):
            if len(user.getUnpaidTransactions()):
                self.return_vars['unpaid_users'].append(user)

    def processPost(self):
        action = self.getPostVariable(name='action', possible_values=['pay_stock', 'credit', 'debit', 'update_user'])
        uid = self.getPostVariable(name='uid', var_type=str)
        user = User.objects.get(uid=uid)
        if action == 'pay_stock':
            amount = self.getPostVariable(name='amount', special=[VariableVerificationTypes.FLOAT_MONEY,
                                                                  VariableVerificationTypes.NON_NEGATIVE],
                                          message='Amount must be specified and be a valid positive amount in pounds')
            # Convert amout from pounds to pence
            amount = int(amount * 100)

            amount, semi_paid_transaction = user.payForStock(author_user=self.getCurrentUserObject(),
                                                             amount=amount)
            if semi_paid_transaction:
                self.return_vars['warning'] = ('Not enough to fully pay transaction: %s' % semi_paid_transaction)
            elif amount:
                self.return_vars['warning'] = ('%s has been added as stock credit to %s' %
                                               (getMoneyString(amount, include_sign=False), uid))

        elif action in ('credit', 'debit'):
            amount = self.getPostVariable(name='amount', special=[VariableVerificationTypes.FLOAT_MONEY,
                                                                  VariableVerificationTypes.POSITIVE],
                                          message='Amount must be specified and be a valid positive amount in pounds')
            # Convert amout from pounds to pence
            amount = int(amount * 100)
            description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True,
                                               message='Description must be less than 255 characters')
            affect_float = self.getPostVariable(name='affect_float', var_type=bool, default=False, set_default=True)
            if action == 'credit':

                user.addCredit(amount=amount, description=description, author=self.getCurrentUserObject(), affect_float=affect_float)
                self.return_vars['info'] = 'Added %s to %s' % (getMoneyString(amount, include_sign=False),
                                                               user.uid)
            elif action == 'debit':
                user.removeCredit(amount=amount, description=description, admin_payment=True, author=self.getCurrentUserObject(),
                                  affect_float=affect_float)
                self.return_vars['info'] = 'Removed %s from %s' % (getMoneyString(amount, include_sign=False),
                                                                   user.uid)
        elif action == 'update_user':
            skype_id = self.getPostVariable(name='skype_id', var_type=str, default=None, set_default=True)
            touchscreen = self.getPostVariable(name='touchscreen', var_type=bool, default=False, set_default=True)
            user.skype_id = skype_id if skype_id != '' else None
            user.touchscreen = touchscreen
            user.save()

