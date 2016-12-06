
from tuckshop.app.models import Transaction, StockPayment, User, Inventory


class TuckStats(object):

    @staticmethod
    def get_current_float():
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
    def get_stock_value():
        """Returns the current sale value of all stock"""
        stock_value = 0
        for item in Inventory.get_all():
            stock_value += item.getStockValue()
        return stock_value

    @staticmethod
    def get_unpaid_stock():
        """Returns the amount owed for stock"""
        owed_amount = 0

        # Iterate over users, aggregating the total amounts
        # owed for stock
        for user in User.get_all():
            owed_amount += user.getTotalOwed()

            # Remove the amount that is present as stock credit
            owed_amount -= user.getStockCreditValue()

        return owed_amount
