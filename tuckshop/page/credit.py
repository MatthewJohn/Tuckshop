import json

from tuckshop.page.page_base import PageBase, VariableVerificationTypes
from tuckshop.core.config import Config
from tuckshop.app.models import Inventory, User
from tuckshop.core.tuckshop_exception import TuckshopException

class Credit(PageBase):
    """Class for displaying the credit page"""

    NAME = 'Credit'
    TEMPLATE = 'credit'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = None

    def processPage(self):
        """Set variables for displaying the credit page"""
        self.return_vars['user'] = self.getCurrentUserObject()
        self.return_vars['enable_custom'] = Config.ENABLE_CUSTOM_PAYMENT()
        self.return_vars['inventory'] = Inventory.getAvailableItemsByPopularity()

        shared_user_data = []
        for user in User.objects.filter(shared=True):
            shared_user_data.append([user.id, user.shared_name])
        self.return_vars['shared_user_data'] = json.dumps(shared_user_data).replace("'", r"\'")

    def processPost(self):
        """Process post requests to credit page"""
        # Obtain post variables
        available_actions = ['pay']
        if Config.ENABLE_CUSTOM_PAYMENT():
            available_actions.append('pay_custom')
        action = self.getPostVariable(name='action', possible_values=available_actions)

        user_object = self.getCurrentUserObject()

        if action == 'pay':
            use_shared_user = self.getPostVariable(name='use_shared_user', var_type=str,
                                                   default=None, set_default=True)

            # Obtain variables to item purchase
            item_id = self.getPostVariable(name='item_id', var_type=int,
                                           special=[VariableVerificationTypes.POSITIVE])
            original_price = self.getPostVariable(name='sale_price', var_type=int,
                                                  special=[VariableVerificationTypes.NON_NEGATIVE])
            inventory_object = Inventory.objects.get(pk=item_id)
            current_user = self.getCurrentUserObject()

            payment_arguments = {
                'inventory': inventory_object,
                'verify_price': original_price,
                'author': current_user
            }

            if use_shared_user:
                payment_arguments['description'] = self.getPostVariable(name='description', var_type=str,
                                                                        message='Description must be less than 255 characters',
                                                                        special=[VariableVerificationTypes.NOT_EMPTY])
                shared_account_ids = [account.id for account in User.objects.filter(shared=True)]
                shared_account_id = self.getPostVariable(name='shared_account', var_type=int, possible_values=shared_account_ids)
                target_user = User.objects.get(pk=shared_account_id)
            else:
                target_user = current_user

            # Perform purchase
            target_user.removeCredit(**payment_arguments)

        elif action == 'pay_custom':
            # Handle custom payment
            amount = self.getPostVariable(name='amount', var_type=int,
                                          special=[VariableVerificationTypes.POSITIVE])
            description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True,
                                               message='Description must be less than 255 characters')
            user_object.removeCredit(amount=amount, description=description, author=user_object)
