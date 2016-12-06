
import os
import marshal
import types
import binascii

from tuckshop.core.celery_con import celery, JOBS
from tuckshop.app.models import Transaction, InventoryTransaction, Inventory, User, StockPayment, StockPaymentTransaction, LOOKUP_OBJECTS
from tuckshop.core.tuck_stats import TuckStats


class Simulation(object):

    def __init__(self, filter_method, filter_vars):
        self.filter_method = binascii.b2a_base64(marshal.dumps(filter_method.func_code))
        self.filter_vars = filter_vars

    @property
    def expire_time(self):
        return 600

    @property
    def job_key(self):
        raise NotImplementedError

    def delete_cache(self):
        if self.job_key in JOBS:
            del(JOBS[self.job_key])

    def start(self):
        if self.job_key not in JOBS:
            JOBS[self.job_key] = self.start_task.apply_async(kwargs={'filter_method': self.filter_method,
                                                                     'filter_vars': self.filter_vars},
                                                             expires=self.expire_time)
        return JOBS[self.job_key]

    @staticmethod
    def setup_data(filter_method, filter_vars):
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


class FloatHistorySimulation(Simulation):

    def __init__(self, name, filter_method, filter_vars):
        self.name = name
        self.filter_method = binascii.b2a_base64(marshal.dumps(filter_method.func_code))
        self.filter_vars = filter_vars

    @property
    def job_key(self):
        return 'history_sim_%s_%s' % (str(self.filter_method), str(self.filter_vars))

    @celery.task(bind=True)
    def start_task(self, filter_method, filter_vars):
        FloatHistorySimulation.setup_data(filter_method, filter_vars)

        return_vars = {}
        from tuckshop.core.tuck_stats import TuckStats
        return_vars['float_amount'], return_vars['total_user_balance'] = TuckStats.get_current_float()
        return_vars['stock_value'] = TuckStats.get_stock_value()
        return_vars['owed'] = TuckStats.get_unpaid_stock()
        return return_vars
