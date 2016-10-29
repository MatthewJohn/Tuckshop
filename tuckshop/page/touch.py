
from tuckshop.app.models import User, Inventory
from tuckshop.page.page_base import PageBase
from tuckshop.core.permission import Permission


class Touch(PageBase):
    NAME = 'TuckShop'
    TEMPLATE = 'touch'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.ACCESS_TOUCH_VIEW


    def processPage(self):
        self.return_vars['users'] = User.objects.filter(shared=False, skype_id__isnull=False).order_by('uid')
        self.return_vars['items'] = []
        # Remove 
        for item in Inventory.getAvailableItemsByPopularity(include_out_of_stock=False):
            if (item.getCurrentInventoryTransaction() and
                    item.getCurrentInventoryTransaction().getQuantityRemaining() and
                    len(self.return_vars['items']) < 23):
                self.return_vars['items'].append(item)

    def processPost(self):
        user_uid = self.getPostVariable(name='username', var_type=str)
        item_id = self.getPostVariable(name='item_id', var_type=int)
        item_sale_price = self.getPostVariable(name='sale_price', var_type=int)
        user = User.objects.get(uid=user_uid)
        item = Inventory.objects.get(pk=item_id)
        user.removeCredit(inventory=item, verify_price=item_sale_price, affect_float=False,
                          author=user)
