"""Contains class for float page"""

from tuckshop.page.page_base import PageBase, VariableVerificationTypes
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.utils import getMoneyString
from tuckshop.app.models import (InventoryTransaction, StockPayment,
                                 Transaction, User, Inventory)
from tuckshop.core.permission import Permission
from tuckshop.core.tuck_stats import TuckStats


class Float(PageBase):

    NAME = 'Float'
    TEMPLATE = 'float'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.FLOAT_ACCESS
    MENU_ORDER = 4
    URL = '/float'

    def processPage(self):
        active_inventory_transactions = InventoryTransaction.getActiveTransactions()
        self.return_vars['active_inventorys'] = []
        for inventory_transaction in active_inventory_transactions:
            if inventory_transaction.inventory not in self.return_vars['active_inventorys']:
                self.return_vars['active_inventorys'].append(inventory_transaction.inventory)

        stock_value = TuckStats.get_stock_value()
        unpaid_stock = TuckStats.get_unpaid_stock()

        float_amount, credit_balance = TuckStats.get_current_float()

        # Calculate what float would be if life were perfect
        float_superficial = float_amount - credit_balance - unpaid_stock + stock_value

        self.return_vars['float'] = getMoneyString(float_amount, include_sign=True)
        self.return_vars['credit_balance'] = getMoneyString(credit_balance, include_sign=True, colour_switch=True)
        self.return_vars['stock_value'] = getMoneyString(stock_value, include_sign=True)
        self.return_vars['stock_owed'] = getMoneyString(unpaid_stock, include_sign=True, colour_switch=True)
        self.return_vars['float_superficial'] = getMoneyString(float_superficial, include_sign=True)

    def processPost(self):
        """There are no post requests handled by the float page"""
        # Obtain common post variables and inventory transaction object
        action = self.getPostVariable(name='action', possible_values=['update_sale_price', 'update_quantity', 'update_cost'])
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

            inventory_transaction_object.updateSalePrice(new_sale_price)

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

        elif action == 'update_cost':
            new_cost = self.getPostVariable(name='cost_price', var_type=float, special=[VariableVerificationTypes.FLOAT_MONEY],
                                            message='Cost price must be a valid amount in pounds, e.g. 1.50')
            new_cost = int(new_cost * 100)
            old_cost = inventory_transaction_object.cost

            if new_cost < inventory_transaction_object.getAmountPaid():
                raise TuckshopException('New Inventory Transaction cost is less than amount that has already been paid')

            inventory_transaction_object.cost = new_cost
            inventory_transaction_object.save()

            self.return_vars['info'] = 'Updated cost of %s from %s to %s' % (inventory_transaction_object.inventory.name,
                                                                             getMoneyString(old_cost), getMoneyString(new_cost))
