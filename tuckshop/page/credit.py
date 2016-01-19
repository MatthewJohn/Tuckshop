from tuckshop.page.page_base import PageBase
from tuckshop.core.config import ENABLE_CUSTOM_PAYMENT
from tuckshop.app.models import Inventory

class Credit(PageBase):

    NAME = 'Credit'
    TEMPLATE = 'credit'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        self.return_vars['user'] = self.getCurrentUserObject()
        self.return_vars['enable_custom'] = ENABLE_CUSTOM_PAYMENT
        self.return_vars['inventory'] = Inventory.getAvailableItems()

    def processPost(self):
        action = self.post_vars['action']
        if (action == 'pay' and 'amount' in self.post_vars):
            if ENABLE_CUSTOM_PAYMENT:
                if 'description' in self.post_vars:
                    description = self.post_vars['description']
                else:
                    description = None
                self.getCurrentUserObject().removeCredit(amount=int(self.post_vars['amount']), description=description)
            else:
                self.return_vars['error'] = 'Custom payment is disabled'
        elif (action == 'pay' and 'item_id' in self.post_vars):
            inventory_object = Inventory.objects.get(pk=self.post_vars['item_id'])
            self.getCurrentUserObject().removeCredit(inventory=inventory_object)
