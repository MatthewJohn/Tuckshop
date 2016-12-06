
import os
import marshal
import types
import binascii

from tuckshop.core.celery_con import celery, JOBS
from tuckshop.app.models import Transaction, InventoryTransaction, Inventory, User, StockPayment, StockPaymentTransaction, LOOKUP_OBJECTS


class HistorySimulation(object):

    def __init__(self, name, filter_method, filter_vars):
        self.name = name
        self.filter_method = binascii.b2a_base64(marshal.dumps(filter_method.func_code))
        self.filter_vars = filter_vars

    @property
    def job_key(self):
        return 'history_sim_%s_%s_%s' % (str(self.name), str(self.filter_method), str(self.filter_vars))

    def delete_cache(self):
        if self.job_key in JOBS:
            del(JOBS[self.job_key])

    def start(self):
        if self.job_key not in JOBS:
            JOBS[self.job_key] = self.start_task.apply_async(kwargs={'name': self.name, 'filter_method': self.filter_method,
                                                                'filter_vars': self.filter_vars})
        return JOBS[self.job_key]

    @celery.task(bind=True)
    def start_task(self, name, filter_method, filter_vars):
        code = marshal.loads(binascii.a2b_base64(filter_method))
        func = types.FunctionType(code, globals(), "some_func_name")
        filter_vars, transactions, users, stock_payments, stock_payment_transactions, inventory_transactions, inventory = func(
            filter_vars=filter_vars,
            transactions=Transaction.objects.all(),
            users=User.objects.all(),
            stock_payments=StockPayment.objects.all(),
            stock_payment_transactions=StockPaymentTransaction.objects.all(),
            inventory_transactions=InventoryTransaction.objects.all(),
            inventory=Inventory.objects.all()
        )
        LOOKUP_OBJECTS['Transaction'] = transactions
        LOOKUP_OBJECTS['User'] = users
        LOOKUP_OBJECTS['StockPayment'] = stock_payments
        LOOKUP_OBJECTS['StockPaymentTransaction'] = stock_payment_transactions
        LOOKUP_OBJECTS['Inventory'] = inventory
        LOOKUP_OBJECTS['InventoryTransaction'] = inventory_transactions

        return_vars = {}
        return_vars['float_amount'], return_vars['total_user_balance'] = HistorySimulation.getCurrentFloat()
        return_vars['stock_value'] = HistorySimulation.getStockValue()
        return_vars['owed'] = HistorySimulation.getUnpaidStock()
        return return_vars

    @staticmethod
    def getCurrentFloat():
        """Gets the current float - amount of money
           in the tuckshop"""
        float_amount = 0
        total_user_balance = 0
        # Get the total amount payed for stock
        for stock_payment in StockPayment.get_all():
            float_amount -= stock_payment.amount

        # Get the total value of payements for items
        for transaction in Transaction.get_all().filter(affect_float=True):
            if transaction.debit:
                float_amount -= transaction.amount
            else:
                float_amount += transaction.amount

        # Adjust float based on user's current credit
        for user in User.get_all():
            total_user_balance += user.getCurrentCredit()

        return float_amount, total_user_balance

    @staticmethod
    def getStockValue():
        """Returns the current sale value of all stock"""
        stock_value = 0
        for item in Inventory.get_all():
            stock_value += item.getStockValue()
        return stock_value

    @staticmethod
    def getUnpaidStock():
        """Returns the amount owed for stock"""
        owed_amount = 0

        # Iterate over users, aggregating the total amounts
        # owed for stock
        for user in User.get_all():
            owed_amount += user.getTotalOwed()

            # Remove the amount that is present as stock credit
            owed_amount -= user.getStockCreditValue()

        return owed_amount
