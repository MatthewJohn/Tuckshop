"""Contains class for stock page"""
import json

from tuckshop.page.page_base import PageBase
from tuckshop.app.models import Inventory, Transaction, InventoryTransaction

class Stock(PageBase):
    """Class for displaying the stock page"""

    NAME = 'Stock'
    TEMPLATE = 'stock'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        """Obtains variables required to display the stock page"""
        self.return_vars['inventory_items'] = Inventory.objects.all().order_by('archive', 'name')
        self.return_vars['active_items'] = Inventory.objects.filter(archive=False)
        self.return_vars['latest_transaction_data'] = json.dumps(
            self.getLatestTransactionData(active_items=self.return_vars['active_items'])
        )

    def getLatestTransactionData(self, active_items):
        """Obtain the latest inventory transactions for recent transaction drop-down"""
        latest_data = {}
        for inventory in active_items:
            latest_data[inventory.id] = []
            transactions = InventoryTransaction.objects.filter(inventory=inventory).order_by('-timestamp')
            duplicate_info_list = []
            for transaction in transactions:
                duplicate_info = '%s_%s_%s_%s' % (transaction.quantity, transaction.sale_price,
                                                  transaction.cost, transaction.description)
                if duplicate_info not in duplicate_info_list:
                    duplicate_info_list.append(duplicate_info)
                    latest_data[inventory.id].append([transaction.id, transaction.quantity,
                                                      float(transaction.cost) / 100,
                                                      transaction.sale_price, transaction.description])
            if (len(latest_data[inventory.id]) == 5):
                break

        return latest_data

    def processPost(self):
        """Handle post requests"""
        action = None if 'action' not in self.post_vars else self.post_vars['action']
        if (action == 'Add Stock'):
            if ('quantity' not in self.post_vars or
                    not int(self.post_vars['quantity'] or
                    int(self.post_vars['quantity']) < 1)):
                self.return_vars['error'] = 'Quantity must be a positive integer'
                return

            quantity = int(self.post_vars['quantity'])
            inventory_id = int(self.post_vars['inv_id'])
            inventory_object = Inventory.objects.get(pk=inventory_id)
            description = None if 'description' not in self.post_vars else str(self.post_vars['description'])

            if (self.post_vars['cost_type'] == 'total'):
                cost = int(float(self.post_vars['cost_total']) * 100)

            elif (self.post_vars['cost_type'] == 'each'):
                cost = (int(float(self.post_vars['cost_each']) * 100) * quantity)

            if ('sale_price' in self.post_vars and self.post_vars['sale_price']):
                sale_price = self.post_vars['sale_price']
            else:
                sale_price = inventory_object.getLatestSalePrice()

            if sale_price is None:
                self.return_vars['error'] = 'No previous stock for item - sale price must be specified'
                return

            inv_transaction = InventoryTransaction(inventory=inventory_object, user=self.getCurrentUserObject(),
                                                   quantity=quantity, cost=cost, sale_price=sale_price,
                                                   description=description)
            inv_transaction.save()
            self.return_vars['info'] = 'Successfully added %s x %s, Cost: %s, Sale Price: %s' % (
                quantity, inventory_object.name, inv_transaction.getCostString(),
                inv_transaction.getSalePriceString()
            )

        elif (action == 'update'):
            if 'item_id' not in self.post_vars:
                self.return_vars['error'] = 'Item ID not available'
                return
            if 'item_name' not in self.post_vars:
                self.return_vars['error'] = 'Item must have a name'
                return
            item = Inventory.objects.get(pk=int(self.post_vars['item_id']))
            item.name = self.post_vars['item_name']
            item.url = None if 'image_url' not in self.post_vars else self.post_vars['image_url']
            item.save()

        elif action == 'archive':
            if 'item_id' not in self.post_vars:
                self.return_vars['error'] = 'Item ID not available'
                return
            item = Inventory.objects.get(pk=int(self.post_vars['item_id']))

            item.archive = (not item.archive)
            item.save()

        elif action == 'delete':
            if 'item_id' not in self.post_vars:
                self.return_vars['error'] = 'Item ID not available'
                return
            item = Inventory.objects.get(pk=int(self.post_vars['item_id']))
            if ((InventoryTransaction.objects.filter(inventory=item) or
                 Transaction.objects.filter(inventory_transaction__inventory=item))):
                self.return_vars['error'] = 'Cannot delete item that has transactions related to it'
                return
            item.delete()

        elif action == 'create':
            if 'item_archive' in self.post_vars:
                archive = bool(self.post_vars['item_archive'])
            else:
                archive = False

            if 'image_url' in self.post_vars:
                image_url = str(self.post_vars['image_url'])
            else:
                image_url = ''

            item = Inventory(name=str(self.post_vars['item_name']), image_url=image_url, archive=archive)
            item.save()
