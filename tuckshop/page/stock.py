"""Contains class for stock page"""
import json

from tuckshop.page.page_base import PageBase, VariableVerificationTypes
from tuckshop.app.models import Inventory, Transaction, InventoryTransaction
from tuckshop.core.tuckshop_exception import TuckshopException

class Stock(PageBase):
    """Class for displaying the stock page"""

    NAME = 'Stock'
    TEMPLATE = 'stock'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        """Obtains variables required to display the stock page"""
        self.return_vars['inventory_items'] = Inventory.objects.all().order_by('archive', 'name')
        self.return_vars['active_items'] = self.return_vars['inventory_items'].filter(archive=False)
        self.return_vars['latest_transaction_data'] = json.dumps(
            self.getLatestTransactionData(active_items=self.return_vars['active_items'])
        ).replace("'", r"\'")

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
        action = self.getPostVariable(name='action', possible_values=['Add Stock', 'update', 'archive',
                                                                      'delete', 'create'])
        if (action == 'Add Stock'):
            quantity = self.getPostVariable(name='quantity', var_type=int,
                                            special=[VariableVerificationTypes.POSITIVE],
                                            message='Quantity must be a positive integer')

            inventory_id = self.getPostVariable(name='inv_id', var_type=int,
                                                special=[VariableVerificationTypes.POSITIVE])
            inventory_object = Inventory.objects.get(pk=inventory_id)


            description = self.getPostVariable(name='description', var_type=str, default=None,
                                               set_default=True)
            cost_type = self.getPostVariable(name='cost_type', var_type=str,
                                             possible_values=['total', 'each'])
            if cost_type == 'total':
                cost_total = self.getPostVariable(name='cost_total', var_type=float,
                                                  special=[VariableVerificationTypes.FLOAT_MONEY,
                                                           VariableVerificationTypes.POSITIVE],
                                                  message='Total cost must be a valid amount in pounds (e.g. 2.12 or 2)')
                cost = int(cost_total * 100)

            elif cost_type == 'each':
                cost_each = self.getPostVariable(name='cost_each', var_type=int,
                                                 special=[VariableVerificationTypes.POSITIVE],
                                                 message='Cost price (each) must be a valid amount in pence (e.g. 30 or 45)')
                cost = (int(cost_each) * quantity)

            sale_price = self.getPostVariable(name='sale_price', var_type=int,
                                              special=[VariableVerificationTypes.POSITIVE],
                                              default=None, set_default=True)
            if not sale_price:
                sale_price = inventory_object.getLatestSalePrice()

            if sale_price is None:
                raise TuckshopException('No previous stock for item - sale price must be specified')

            inv_transaction = InventoryTransaction(inventory=inventory_object, user=self.getCurrentUserObject(),
                                                   quantity=quantity, cost=cost, sale_price=sale_price,
                                                   description=description)
            inv_transaction.save()
            self.return_vars['info'] = 'Successfully added %s x %s, Cost: %s, Sale Price: %s' % (
                quantity, inventory_object.name, inv_transaction.getCostString(),
                inv_transaction.getSalePriceString()
            )

        elif (action == 'update'):
            # Obtain POST variables for updating an item
            item_id = self.getPostVariable(name='item_id', var_type=int,
                                           special=[VariableVerificationTypes.POSITIVE])
            item_name = self.getPostVariable(name='item_name', var_type=str,
                                             special=[VariableVerificationTypes.NOT_EMPTY],
                                             message='Item must have a name')
            image_url = self.getPostVariable(name='image_url', var_type=str,
                                             default='', set_default=True)

            # Obtain item object
            item = Inventory.objects.get(pk=item_id)

            # Ensure that there is not already a inventory item with the same name
            duplicate_names = Inventory.objects.filter(name=item_name).exclude(pk=item.pk)
            if len(duplicate_names):
                raise TuckshopException('Item already exists with this name')

            # Update item with new values
            item.name = item_name
            item.image_url = image_url
            item.save()

            self.return_vars['info'] = 'Successfully updated item %s' % item.name

        elif action == 'archive':
            # Obtain item ID from POST variables
            item_id = self.getPostVariable(name='item_id', var_type=int,
                                           special=[VariableVerificationTypes.POSITIVE])

            item = Inventory.objects.get(pk=item_id)

            # Reverse the item's archive status
            item.archive = (not item.archive)
            item.save()

            archive_action = 'archived' if item.archive else 'un-archived'
            self.return_vars['info'] = 'Successfully %s item \'%s\'' % (archive_action, item.name)

        elif action == 'delete':
            # Obtain POST variables for updating an item
            item_id = self.getPostVariable(name='item_id', var_type=int,
                                           special=[VariableVerificationTypes.POSITIVE])

            item = Inventory.objects.get(pk=item_id)
            item_name = item.name

            # Determine if the item exists and whether it has any related
            # inventory_transactions
            if ((InventoryTransaction.objects.filter(inventory=item) or
                 Transaction.objects.filter(inventory_transaction__inventory=item))):
                raise TuckshopException('Cannot delete item that has transactions related to it')

            # Delete the item
            item.delete()

            self.return_vars['info'] = 'Successfully removed item \'%s\'' % item_name

        elif action == 'create':
            # Obtain values for new item from POST variables
            item_name = self.getPostVariable(name='item_name', var_type=str,
                                             special=[VariableVerificationTypes.NOT_EMPTY],
                                             message='Item must have a name')
            image_url = self.getPostVariable(name='image_url', var_type=str,
                                             default='', set_default=True)
            archive = self.getPostVariable(name='item_archive', var_type=bool,
                                           default=False, set_default=True)

            # Ensure that there is not already a inventory item with the same name
            duplicate_names = Inventory.objects.filter(name=item_name)
            if len(duplicate_names):
                raise TuckshopException('Item already exists with this name')

            # Create new item
            item = Inventory(name=item_name, image_url=image_url, archive=archive)
            item.save()

            self.return_vars['info'] = 'Successfully created item \'%s\'' % item_name
