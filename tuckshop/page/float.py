"""Contains class for float page"""

from tuckshop.page.page_base import PageBase
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
        pass

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