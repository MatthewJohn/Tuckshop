"""Contains class for float page"""

from tuckshop.page.page_base import PageBase
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.utils import getMoneyString
from tuckshop.app.models import (InventoryTransaction, StockPayment,
                                 Transaction, User, Inventory)

class Float(PageBase):

    NAME = 'Float'
    TEMPLATE = 'float'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = True

    def processPage(self):
        active_inventory_transactions = InventoryTransaction.getActiveTransactions()
        self.return_vars['active_inventorys'] = []
        for inventory_transaction in active_inventory_transactions:
            if inventory_transaction.inventory not in self.return_vars['active_inventorys']:
                self.return_vars['active_inventorys'].append(inventory_transaction.inventory)

        float_amount, credit_balance = self.getCurrentFloat()
        self.return_vars['float'] = getMoneyString(float_amount, include_sign=True)
        self.return_vars['credit_balance'] = getMoneyString(credit_balance, include_sign=True, colour_switch=True)
        self.return_vars['stock_value'] = getMoneyString(self.getStockValue(), include_sign=True)
        self.return_vars['stock_owed'] = getMoneyString(self.getUnpaidStock(), include_sign=True, colour_switch=True)

    def processPost(self):
        """There are no post requests handled by the float page"""
        action = None if 'action' not in self.post_vars else self.post_vars['action']
        inventory_transaction_id = None if 'inventory_transaction_id' not in self.post_vars else self.post_vars['inventory_transaction_id']
        try:
            inventory_transaction_id = int(inventory_transaction_id)
        except:
            raise TuckshopException('Transaction ID must an integer')
        inventory_transaction_object = InventoryTransaction.objects.get(pk=inventory_transaction_id)
        if action == 'update_sale_price':
            # Ensure sale price is valid
            if 'sale_price' not in self.post_vars or int(self.post_vars['sale_price']) < 0:
                raise TuckshopException('Sale price must be a positive integer in pence')

            # Ensure that there are remaining available items in the transaction to change the price for
            if not inventory_transaction_object.getQuantityRemaining():
                raise TuckshopException('There are no remaining items in the inventory transaction')

            old_sale_price = inventory_transaction_object.sale_price
            new_sale_price = int(self.post_vars['sale_price'])
            remaining_quantity = inventory_transaction_object.getQuantityRemaining()

            if inventory_transaction_object.getQuantitySold():
                # If any of the items have been sold, create a new transaction for the
                # items remaining
                inventory_transaction_object.quantity -= remaining_quantity
                inventory_transaction_object.save()

                # Create a new inventory transaction for the new item
                new_inventory_transaction = InventoryTransaction.objects.get(pk=inventory_transaction_object.pk)
                new_inventory_transaction.pk = None
                new_inventory_transaction.quantity = remaining_quantity
                new_inventory_transaction.sale_price = new_sale_price
                new_inventory_transaction.save()

                # Update the timestamp of the new inventory transaction, as it will
                # default to the current time when created
                new_inventory_transaction.timestamp = inventory_transaction_object.timestamp
                new_inventory_transaction.save()
            else:
                # Else Simply update the transaction
                inventory_transaction_object.sale_price = new_sale_price
                inventory_transaction_object.save()

            self.return_vars['info'] = ('Updated sale price of %s items from %sp to %sp' %
                                        (remaining_quantity, old_sale_price,
                                         new_sale_price))

        elif action == 'update_quantity':
            # Ensure sale price is valid
            if 'quantity' not in self.post_vars or int(self.post_vars['quantity']) < 0:
                raise TuckshopException('Sale price must be a positive integer in pence')
            new_quantity = int(self.post_vars['quantity'])
            old_quantity = inventory_transaction_object.quantity

            # Ensure that there are remaining available items in the transaction to change the price for
            if inventory_transaction_object.getQuantitySold() > new_quantity:
                raise TuckshopException('The new quantity (%s) is less than the amount sold (%s)' %
                                        (new_quantity, inventory_transaction_object.getQuantitySold()))

            # Update the quantity of the sale transaction
            inventory_transaction_object.quantity = new_quantity
            inventory_transaction_object.save()

            self.return_vars['info'] = ('Updated quantity from %s to %s (%s now available)' %
                                        (old_quantity, new_quantity,
                                         inventory_transaction_object.getQuantityRemaining()))


    def getCurrentFloat(self):
        """Gets the current float - amount of money
           in the tuckshop"""
        float_amount = 0
        total_user_balance = 0
        # Get the total amount payed for stock
        for stock_payment in StockPayment.objects.all():
            float_amount -= stock_payment.amount

        # Get the total value of payements for items (transactions with linked inventory items)
        for transaction in Transaction.objects.filter(inventory_transaction__isnull=False):
            float_amount += transaction.amount

        # Adjust float based on user's current credit
        for user in User.objects.all():
            user_current_credit = user.getCurrentCredit()
            float_amount += user.getCurrentCredit()
            total_user_balance += user.getCurrentCredit()

        return float_amount, total_user_balance

    def getStockValue(self):
        """Returns the current sale value of all stock"""
        stock_value = 0
        for item in Inventory.objects.all():
            stock_value += item.getStockValue()
        return stock_value

    def getUnpaidStock(self):
        """Returns the amount owed for stock"""
        owed_amount = 0
        for user in User.objects.all():
            owed_amount += user.getTotalOwed()
        return owed_amount
