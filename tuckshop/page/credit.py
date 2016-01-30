from tuckshop.page.page_base import PageBase, VariableVerificationTypes
from tuckshop.core.config import Config
from tuckshop.app.models import Inventory
from tuckshop.core.tuckshop_exception import TuckshopException

class Credit(PageBase):
    """Class for displaying the credit page"""

    NAME = 'Credit'
    TEMPLATE = 'credit'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        """Set variables for displaying the credit page"""
        self.return_vars['user'] = self.getCurrentUserObject()
        self.return_vars['enable_custom'] = Config.ENABLE_CUSTOM_PAYMENT()
        self.return_vars['inventory'] = Inventory.getAvailableItemsByPopularity()

    def processPost(self):
        """Process post requests to credit page"""
        # Obtain post variables
        available_actions = ['pay']
        if Config.ENABLE_CUSTOM_PAYMENT():
            available_actions.append('pay_custom')
        action = self.getPostVariable(name='action', possible_values=available_actions)

        user_object = self.getCurrentUserObject()

        if action == 'pay':
            # Obtain variables to item purchase
            item_id = self.getPostVariable(name='item_id', var_type=int,
                                           special=[VariableVerificationTypes.POSITIVE])
            original_price = self.getPostVariable(name='sale_price', var_type=int,
                                                  special=[VariableVerificationTypes.NON_NEGATIVE])
            inventory_object = Inventory.objects.get(pk=item_id)

            # Perform purchase
            user_object.removeCredit(inventory=inventory_object, verify_price=original_price)

        elif action == 'pay_custom':
            # Handle custom payment
            amount = self.getPostVariable(name='amount', var_type=int,
                                          special=[VariableVerificationTypes.POSITIVE])
            description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True,
                                               message='Description must be less than 255 characters')
            user_object.removeCredit(amount=amount, description=description)
