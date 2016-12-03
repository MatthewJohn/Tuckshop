"""Contains class for graph page"""

import json
from datetime import datetime, timedelta

from tuckshop.page.page_base import PageBase, VariableVerificationTypes
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.utils import getMoneyString
from tuckshop.app.models import (InventoryTransaction, StockPayment,
                                 Transaction, User, Inventory)
from tuckshop.core.simulation import HistorySimulation
from tuckshop.core.permission import Permission


class Graph(PageBase):

    NAME = 'Graph'
    TEMPLATE = 'graph'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.FLOAT_ACCESS
    MENU_ORDER = 4
    URL = '/graph'

    def processPage(self):
        def filter_data(filter_vars, transactions, users, stock_payments, stock_payment_transactions, inventory_transactions, inventory):
            import datetime
            transactions = transactions.filter(timestamp__lt=datetime.date(filter_vars['year'], filter_vars['month'], filter_vars['day']))
            stock_payments = stock_payments.filter(timestamp__lt=datetime.date(filter_vars['year'], filter_vars['month'], filter_vars['day']))
            stock_payment_transactions = stock_payment_transactions.filter(timestamp__lt=datetime.date(filter_vars['year'], filter_vars['month'], filter_vars['day']))
            return filter_vars, transactions, users, stock_payments, stock_payment_transactions, inventory_transactions, inventory

        not_enough_data = 0
        float_amount = ['Float']
        total_user_balance = ['User Credit']
        stock_value = ['Stock Value']
        owed = ['Owed Stock']
        sup_float = ['Superficial Float']
        for days_back in list(reversed(range(1, 29))):
            d = datetime.today() - timedelta(days=days_back)
            sim = HistorySimulation(name='test', filter_method=filter_data, filter_vars={'year': d.year, 'month': d.month, 'day': d.day})
            cel = sim.start()
            if cel.successful():
                data = cel.get(timeout=1)
                float_amount.append(float(data['float_amount']/100.0))
                total_user_balance.append(float(data['total_user_balance']/100.0))
                stock_value.append(float(data['stock_value']/100.0))
                owed.append(float(data['owed']/100.0))
                sup_float.append(float((((data['float_amount'] - data['total_user_balance']) - data['owed']) + data['stock_value'])/100.0))
            elif cel.state == 'FAILURE':
                sim.delete_cache()
                sim.start()
                not_enough_data += 1
            else:
                not_enough_data += 1

        self.return_vars['graph_data'] = json.dumps([float_amount, total_user_balance, stock_value, owed, sup_float]) if not not_enough_data else None
        self.return_vars['not_enough_data'] = not_enough_data

