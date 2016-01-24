"""Contains class for float page"""

from tuckshop.page.page_base import PageBase, VariableVerificationTypes
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
        # Obtain common post variables and inventory transaction object
        action = self.getPostVariable(name='action', possible_values=['update_sale_price', 'update_quantity'])
        inventory_transaction_id = self.getPostVariable(name='inventory_transaction_id', var_type=int,
                                                        special=[VariableVerificationTypes.POSITIVE])
        inventory_transaction_object = InventoryTransaction.objects.get(pk=inventory_transaction_id)

        if action == 'update_sale_price':
            # Ensure sale price is valid
            new_sale_price = self.getPostVariable(name='sale_price', var_type=int,
                                                  special=[VariableVerificationTypes.POSITIVE],
                                                  message='Sale price must be a positive integer in pence')

            # Ensure that there are remaining available items in the transaction to change the price for
            if not inventory_transaction_object.getQuantityRemaining():
                raise TuckshopException('There are no remaining items in the inventory transaction')

            old_sale_price = inventory_transaction_object.sale_price
            remaining_quantity = inventory_transaction_object.getQuantityRemaining()

            if inventory_transaction_object.getQuantitySold():
                # If any of the items have been sold, create a new transaction for the
                # items remaining
                inventory_transaction_object.quantity -= remaining_quantity
                inventory_transaction_object.save()

                # Create a new inventory transaction for the new item
                new_inventory_transaction = InventoryTransaction.objects.get(pk=inventory_transaction_object.pk)
                new_inventory_transaction.pk = None
                # Update the quantity to reflect the quantity of items being
                # updated
                new_inventory_transaction.quantity = remaining_quantity
                new_inventory_transaction.sale_price = new_sale_price

                # Set the cost to 0, as the cost is captured in the original
                # inventory transaction
                new_inventory_transaction.cost = 0
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
            new_quantity_remaining = self.getPostVariable(name='quantity', var_type=int,
                                                          message='Quantity must be a non-negative integer',
                                                          special=[VariableVerificationTypes.NON_NEGATIVE])

            # Determine the new quantity using the amount already sold and the new
            # amount unsold, by the user.
            old_quantity = inventory_transaction_object.quantity
            new_quantity = inventory_transaction_object.getQuantitySold() + new_quantity_remaining

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
