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
        action = self.getPostVariable(name='action', possible_values=['pay'])

        item_id = self.getPostVariable(name='item_id', default=None, set_default=True, var_type=int,
                                       special=[VariableVerificationTypes.POSITIVE])
        amount = self.getPostVariable(name='amount', default=None, set_default=True, var_type=int,
                                      special=[VariableVerificationTypes.POSITIVE])
        if action == 'pay':
            user_object = self.getCurrentUserObject()
            if amount:
                description = self.getPostVariable(name='description', var_type=str, default=None, set_default=True,
                                                   message='Description must be less than 255 characters')

                if Config.ENABLE_CUSTOM_PAYMENT():
                    user_object.removeCredit(amount=amount, description=description)
                else:
                    raise TuckshopException('Custom payment is disabled')
            elif item_id:
                original_price = self.getPostVariable(name='sale_price', var_type=int,
                                                      special=[VariableVerificationTypes.NON_NEGATIVE])
                inventory_object = Inventory.objects.get(pk=item_id)

                user_object.removeCredit(inventory=inventory_object, verify_price=original_price)
            elif Config.ENABLE_CUSTOM_PAYMENT():
                raise TuckshopException('Amount must be specified')
            else:
                raise Exception('Item ID was not specified')
