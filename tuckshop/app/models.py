from django.db import models, transaction as DbTransaction
from enum import Enum
import ldap
from decimal import Decimal
import datetime
from os import environ

from tuckshop.core.config import Config
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.redis_connection import RedisConnection
from tuckshop.core.utils import getMoneyString
from tuckshop.core.image import Image
from tuckshop.core.skype import Skype
from tuckshop.core.permission import Permission


LOOKUP_OBJECTS = {
    'User': None,
    'Inventory': None,
    'InventoryTransaction': None,
    'Transaction': None,
    'StockPayment': None,
    'StockPaymentTransaction': None
}

class LookupModel(models.Model):
    @classmethod
    def get_all(cls):
        if LOOKUP_OBJECTS[cls.__name__]:
            return LOOKUP_OBJECTS[cls.__name__]
        else:
            return cls.objects.all()

    class Meta:
        abstract = True

def default_permission():
    permission = 0
    for permission_enum in Permission.get_default_permission():
        permission_bit = 1 << permission_enum.value
        permission &= ~permission_bit
    return permission

class User(LookupModel):

    uid = models.CharField(max_length=10)
    admin = models.BooleanField(default=False)
    permissions = models.IntegerField(default=default_permission())
    timestamp = models.DateTimeField(auto_now_add=True)
    shared = models.BooleanField(default=False)
    shared_name = models.CharField(max_length=255, null=True)
    skype_id = models.CharField(max_length=64, null=True)
    touchscreen = models.BooleanField(default=False)

    current_credit_cache_key = 'User_%s_credit'

    def __init__(self, *args, **kwargs):

        user_object = super(User, self).__init__(*args, **kwargs)

        if self.shared:
            self.dispaly_name = self.shared_name
        elif not ('TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']):
            # Obtain information from LDAP
            ldap_obj = ldap.initialize('ldap://%s:389' % Config.LDAP_SERVER())
            dn = 'uid=%s,%s' % (self.uid, Config.LDAP_USER_BASE())
            ldap_obj.simple_bind_s()
            res = ldap_obj.search_s(Config.LDAP_USER_BASE(), ldap.SCOPE_ONELEVEL,
                                    'uid=%s' % self.uid, ['mail', 'givenName'])

            if (not res):
                raise Exception('User \'%s\' does not exist in LDAP' % self.uid)

            self.dn = res[0][0]
            self.display_name = res[0][1]['givenName'][0]
            self.email = res[0][1]['mail'][0]
        else:
            self.dn = 'uid=test'
            self.display_name = 'Test User'
            self.email = 'test@example.com'
            if (self.uid == 'aa'):
                self.admin = True

    def getStockCreditValue(self, string=False, none_on_zero=False):
        """Obtains the total stock credit the user has"""
        credit = 0
        for stock_payment in self.getStockCredit():
            credit += stock_payment.amount

        if credit == 0 and none_on_zero:
            return None

        if string:
            return getMoneyString(credit, include_sign=False)
        else:
            return credit

    def getStockCredit(self):
        """Returns the stock payments objects for credit"""
        return StockPayment.get_all().filter(user=self, inventory_transaction__isnull=True)

    @DbTransaction.atomic
    def payForStock(self, author_user, amount):
        # Ensure that amount is a positive integer (or 0)
        if amount < 0:
            raise Exception('Amount must be a positive amount')

        def payUsingCredit(transaction):
            # Iterate through credit payments, and attampt to pay
            # for unpaid stock
            for credit_stock_payment in self.getStockCredit():
                credit_amount = credit_stock_payment.amount
                due_amount = transaction.getRemainingCost()

                # If the amount due to the transaction is less than is available
                # in the credit, split the credit, so that the amount remaining on
                # the transaction can be payed off.
                if due_amount < credit_amount:
                    remainder_stock_credit = StockPayment.get_all().get(pk=credit_stock_payment.pk)
                    remainder_stock_credit.pk = None
                    remainder_stock_credit.amount = int(credit_amount - due_amount)
                    remainder_stock_credit.save()

                    # Update the old stock payment to match the amount due for the transaction
                    credit_stock_payment.amount = transaction.getRemainingCost()
                    credit_stock_payment.save()

                # Assign the credit to the inventory transaction
                credit_stock_payment.inventory_transaction = transaction
                credit_stock_payment.save()

                # If the transaction has been paid off, return True
                if credit_amount >= due_amount:
                    return True
            # Otherwise if the transaction was not payed off, return False
            return False

        if self.skype_id:
            Skype.get_object().send_message.delay(
                self.skype_id,
                'Paid for stock: ' +
                getMoneyString(amount, include_sign=False, symbol=u"\xA3") +
                ' (including credit)'
            )
        semi_paid_transaction = None
        stock_payment_transaction = None

        for transaction in self.getUnpaidTransactions():
            if payUsingCredit(transaction):
                continue

            # Create a stock payement transaction if one has not already been created
            if not stock_payment_transaction:
                stock_payment_transaction = StockPaymentTransaction(author=author_user, user=self)
                stock_payment_transaction.save()

            # Since the transaction couldn't be paid with credit,
            # start using the amount paid
            transaction_amount = 0

            # If the remaining cost of the transaction is more than
            # the amount remainig available to pay, create a StockPayment
            # for the remaining amount in the stock payment transaction.
            if transaction.getRemainingCost() > amount:
                transaction_amount = amount
                semi_paid_transaction = transaction
            else:
                transaction_amount = transaction.getRemainingCost()

            StockPayment(user=self, inventory_transaction=transaction, amount=transaction_amount,
                         stock_payment_transaction=stock_payment_transaction).save()
            transaction.save()

            amount -= transaction_amount
            if amount == 0:
                break

        # If there is still funds left in the amount
        # paid to the buyer, create a blank stock payment,
        # which can be used in future to pay off stock
        if amount:
            # Create a stock payement transaction if one has not already been created
            if not stock_payment_transaction:
                stock_payment_transaction = StockPaymentTransaction(author=author_user, user=self)
                stock_payment_transaction.save()

            StockPayment(user=self, amount=amount,
                         stock_payment_transaction=stock_payment_transaction).save()

        return amount, semi_paid_transaction

    def getTotalOwed(self):
        amount_owned = 0
        for unpaid_transaction in self.getUnpaidTransactions():
            amount_owned += unpaid_transaction.getRemainingCost()
        return amount_owned

    def getTotalOwedString(self):
        return getMoneyString(self.getTotalOwed(), include_sign=False)

    def getUnpaidTransactions(self):
        # Would use the following, however, the Sum annotation cannot be used to filter
        # InventoryTransaction.objects.filter(user=self).annotate(amount_paid=models.Sum('stockpayment__amount')).order_by('-amount_paid', 'timestamp')
        inventory_transactions = []
        for inventory_transaction in InventoryTransaction.get_all().filter(user=self):
            if inventory_transaction.getRemainingCost():
                inventory_transactions.append(inventory_transaction)
        inventory_transactions.sort(key=lambda x: (-x.getAmountPaid(), bool(x.getQuantityRemaining()), x.timestamp))
        return inventory_transactions

    def getCurrentCredit(self, refresh_cache=False, transactions=None):
        if (refresh_cache or LOOKUP_OBJECTS['Transaction'] or
                not RedisConnection.exists(User.current_credit_cache_key % self.id)):
            balance = 0
            user_transactions = Transaction.get_all()
            for transaction in user_transactions.filter(user=self):
                if (transaction.debit):
                    balance -= transaction.amount
                else:
                    balance += transaction.amount

            if not LOOKUP_OBJECTS['Transaction']:
                # Update cache
                RedisConnection.set(User.current_credit_cache_key % self.id, balance)
        else:
            # Obtain credit from cache
            balance = int(RedisConnection.get(User.current_credit_cache_key % self.id))
        return balance

    @DbTransaction.atomic
    def addCredit(self, amount, author, affect_float, description=None):
        amount = int(amount)
        if (amount < 0):
            raise Exception('Cannot use negative number')
        current_credit = self.getCurrentCredit()
        transaction = Transaction(user=self, amount=amount, debit=False, description=description,
                                  payment_type=Transaction.TransactionType.ADMIN_CHANGE.value,
                                  author=author, affect_float=affect_float)
        transaction.save()

        # Update credit cache
        current_credit += amount
        RedisConnection.set(User.current_credit_cache_key % self.id,
                            current_credit)

        if self.skype_id:
            try:
                Skype.get_object().send_message.delay(
                    self.skype_id,
                    'Credit added: ' + getMoneyString(
                        amount,
                        include_sign=False,
                        symbol=u"\xA3"))
            except:
                pass

        return current_credit

    @DbTransaction.atomic
    def removeCredit(self, affect_float, amount=None, inventory=None, description=None,
                     verify_price=None, admin_payment=False, author=None):
        if author is None:
            raise TuckshopException('Author must be specified for credit changes')

        if (inventory and inventory.getQuantityRemaining() <= 0):
            raise TuckshopException('There are no items in stock')

        if inventory and inventory.archive:
            raise TuckshopException('Item is archived')

        current_credit = self.getCurrentCredit()
        transaction = Transaction(user=self, debit=True, author=author)

        if admin_payment:
            skype_message = 'An admin has added money to your account: '
            payment_type = Transaction.TransactionType.ADMIN_CHANGE.value
        else:
            payment_type = Transaction.TransactionType.CUSTOM_PAYMENT.value
            skype_message = 'You made a custom payment: '

        if (inventory):
            payment_type = Transaction.TransactionType.ITEM_PURCHASE.value
            inventory_transaction = inventory.getCurrentInventoryTransaction()
            if inventory_transaction is None:
                raise TuckshopException('No inventory transaction available for this item')

            transaction.inventory_transaction = inventory_transaction


            if (not amount):
                amount = inventory_transaction.sale_price

                # If a verification price has been supplied,
                # ensure the price being paid for the item matches.
                if verify_price is not None and amount != verify_price:
                    raise TuckshopException('Purchase cancelled - Price has changed from %s to %s' %
                                            (getMoneyString(verify_price, include_sign=False),
                                             getMoneyString(amount, include_sign=False)))
            skype_message = inventory.name + ' purchased: '

        elif not amount:
            raise TuckshopException('Must pass amount or inventory')

        amount = int(amount)
        if (amount < 0):
            raise TuckshopException('Cannot use negative number')

        transaction.payment_type = payment_type
        transaction.amount = amount
        transaction.description = description
        transaction.affect_float = affect_float
        transaction.save()

        # Update credit cache
        current_credit -= amount
        RedisConnection.set(User.current_credit_cache_key % self.id,
                            current_credit)

        skype_message += getMoneyString(amount, include_sign=False,
                                        symbol=u"\xA3")
        skype_message += ("\nReason: " + description) if description else ''
        skype_message += "\nNew Credit: " + getMoneyString(current_credit, include_sign=False,
                                                           symbol=u"\xA3")
        if self.skype_id:
            Skype.get_object().send_message.delay(self.skype_id, skype_message)

        return current_credit

    def getCreditString(self):
        return getMoneyString(self.getCurrentCredit())

    def getTransactionHistory(self, date_from=None, date_to=None, author=False):
        parameters = {}
        if date_from is None:
            date_from = datetime.datetime.fromtimestamp(0)
        parameters['timestamp__gt'] = date_from

        if date_to is None:
            date_to = datetime.datetime.now()
        parameters['timestamp__lt'] = date_to

        transactions = Transaction.get_all()

        if author:
            parameters['author'] = self
            parameters['user__shared'] = True
            transactions = transactions.exclude(user=self)
        else:
            parameters['user'] = self

        return transactions.filter(**parameters)

    def getStockPayments(self):
        return StockPayment.get_all().filter(user=self)

    def getStockPaymentTransactions(self):
        return StockPaymentTransaction.get_all().filter(user=self)

    @property
    def isAdmin(self):
        return self.admin

    @property
    def _permissionValue(self):
        return self.permissions

    def setAdmin(self):
        self.admin = True
        self.save()

    def removeAdmin(self):
        self.admin = False
        self.save()

    def addPermission(self, permission):
        permission_bit = 1 << permission.value
        self.permissions |= permission_bit
        self.save()

    def removePermission(self, permission):
        permission_bit = 1 << permission.value
        self.permissions &= ~permission_bit
        self.save()

    def checkPermission(self, permission):
        """Determines if the user has a specified permission"""
        # If the user is an admin, return True -
        # Users can do EVERYTHING
        if self.isAdmin:
            return True

        permission_bit = 1 << permission.value
        return bool(self._permissionValue & permission_bit)


class Inventory(LookupModel):
    name = models.CharField(max_length=200)
    bardcode_number = models.CharField(max_length=25, null=True)
    image_url = models.CharField(max_length=250, null=True)
    archive = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    inventory_transaction_cache_key = 'Inventory_%s_inventory_transaction'

    def getStockValue(self):
        """Returns the total sale value for the available stock"""
        total_value = 0
        for inv_transaction in InventoryTransaction.get_all().filter(inventory=self):
            total_value += (inv_transaction.getQuantityRemaining() * inv_transaction.sale_price)

        return total_value

    def getSalePrice(self):
        if self.getCurrentInventoryTransaction():
            return self.getCurrentInventoryTransaction().sale_price
        else:
            return None

    def getQuantityRemaining(self, include_all_transactions=True):
        if (include_all_transactions):
            quantity = 0
            for transaction in InventoryTransaction.get_all().filter(inventory=self):
                quantity += transaction.getQuantityRemaining()
        else:
            quantity = self.getCurrentInventoryTransaction().getQuantityRemaining()
        return quantity

    def get_stock_end_date(self):
        # Determine if there are enough purchases to determine a sensible date
        if Transaction.get_all().filter(inventory_transaction__inventory=self).count() < 20:
            return None

        # Obtain inventory transactions for last 3 months
        inv_transactions = []
        transaction_count = 0
        for transaction in Transaction.get_all().filter(inventory_transaction__inventory=self, timestamp__gt=(datetime.datetime.now() - datetime.timedelta(days=3*365/12))):
            if transaction.inventory_transaction not in inv_transactions:
                inv_transactions.append(transaction.inventory_transaction)
                transaction_count += transaction.inventory_transaction.getQuantitySold()

        # If there are not enough transactions, obtain more from prevous inventory transasctions
        if transaction_count < 15:
            for inventory_transaction in InventoryTransaction.get_all().filter(inventory=self).order_by('-timestamp'):
                if inventory_transaction not in inv_transactions:
                    inv_transactions.append(inventory_transaction)
                    transaction_count += inventory_transaction.getQuantitySold()

                if transaction_count >=15:
                    break
            else:
                return None 

        # Determine average stock depletion duration and mean burn rate
        stock_dep_mean = 0
        burn_mean = 0
        dep_transactions = 0
        burn_transactions = 0
        for inv_transaction in inv_transactions:
            dep_duration = inv_transaction.get_dep_duration()
            if dep_duration is not None:
                stock_dep_mean += inv_transaction.get_dep_duration()
                dep_transactions += 1

            burn_rate = inv_transaction.get_burn_rate()
            if burn_rate is not None:
                burn_mean += (burn_rate / (60 * 24))
                burn_transactions += 1

        stock_dep_mean /= dep_transactions
        burn_mean /= burn_transactions
        if stock_dep_mean:
            stock_dep_rate = (1 / stock_dep_mean) * self.getQuantityRemaining(include_all_transactions=True)
        else:
            stock_dep_rate = None
        if burn_mean:
            stock_burn_rate = burn_mean * self.getQuantityRemaining(include_all_transactions=True)
        else:
            stock_burn_rate = None
        return stock_dep_rate, stock_burn_rate

        # For last 3 inv transactions, determine predicted and actual run out date, then create multiplier

        # Determine burn rate corelation, to determine if accelerating or deccelerating

        # Determine burn rate aceleration, using all transactions

        # Determine if end date calculated by the mean burn rate, after being updated from the burn rate acceleration,
        # is too different from the mean burn rate and average stock depletion duration


    def getCurrentInventoryTransaction(self, refresh_cache=False):
        cache_key = Inventory.inventory_transaction_cache_key % self.id
        cache_exists = RedisConnection.exists(cache_key)

        # If the cache if to be refreshed or the cache has not been set,
        # calculate the current inventory transaction for the item
        if (refresh_cache or not cache_exists or LOOKUP_OBJECTS['InventoryTransaction']):

            # Iterate through the inventory transactions for this item
            for transaction in InventoryTransaction.get_all().filter(inventory=self).order_by('timestamp'):

                # If the transaction has items left, set this as the current
                # transaction and return it
                if (transaction.getQuantityRemaining() and not LOOKUP_OBJECTS['InventoryTransaction']):
                    RedisConnection.set(cache_key, transaction.id)
                    return transaction

            # If no active transaction were found, clear the cache and
            # return with None
            if cache_exists and not LOOKUP_OBJECTS['InventoryTransaction']:
                RedisConnection.delete(cache_key)
            return None
        else:
            transaction = InventoryTransaction.get_all().get(pk=RedisConnection.get(cache_key))

            # Ensure that the transaction has items left
            if (transaction.getQuantityRemaining()):
                # If so, return the transaction
                return transaction
            else:
                # Otherwise, clear the cache and use this function to search for a new
                # transaction
                return self.getCurrentInventoryTransaction(refresh_cache=True)

    def getInventoryTransactions(self, only_active=True):
        inventory_transactions_qs = InventoryTransaction.get_all().filter(inventory=self)
        inventory_transactions = []
        for inventory_transaction in inventory_transactions_qs:
            if inventory_transaction.getQuantityRemaining() or not only_active:
                inventory_transactions.append(inventory_transaction)

        return inventory_transactions

    def getImageObject(self):
        return Image(self)

    @staticmethod
    def getAvailableItems():
        """Returns the available items"""
        items = Inventory.get_all().filter(archive=False)
        # If out of stock items are not show, filter
        # them from the query
        if not Config.SHOW_OUT_OF_STOCK_ITEMS():
            for item in items:
                if (not item.getCurrentInventoryTransaction().getQuantityRemaining()):
                    items.remove(item)

        return items

    def getTransactionCount(self):
        """Returns the number of transaction for the item"""
        return len(Transaction.get_all().filter(inventory_transaction__inventory=self))

    @staticmethod
    def getAvailableItemsByPopularity(include_out_of_stock=True):
        """Returns available items, sorted by popularity"""
        items = Inventory.getAvailableItems()

        # Anotate the results with the number of transactions
        items = items.annotate(transaction_count=models.Count('inventorytransaction__transaction'))

        # Convert query set to list, so that they can be sorted
        items = [item for item in items]

        # Sort by:
        # 1. Whether the item has ever had any stock
        # 2. Whether the item is in stock
        # 3. The number of transactions (popularity)
        # 4. Timestamp
        items.sort(key=lambda x: (bool(x.getInventoryTransactions(only_active=False)),
                                  bool(x.getQuantityRemaining()),
                                  x.getTransactionCount(),
                                  x.timestamp),
                   reverse=True)

        # Return the ordered results
        return items

    def getSalePriceString(self):
        # Attempt to get the price from the current transaction
        price = self.getSalePrice()

        if price is None:
            # If there is no current transaction, return the price
            # from the last transaction
            transactions = InventoryTransaction.get_all().filter(inventory=self).order_by('-timestamp')
            if len(transactions):
                return getMoneyString(transactions[0].sale_price, include_sign=False)
            else:
                return 'N/A'

        else:
            return getMoneyString(price, include_sign=False)

    def getPriceRangeString(self):
        inventory_transactions = InventoryTransaction.get_all().filter(inventory=self).order_by('sale_price')
        inventory_transaction_list = []
        for inventory_transaction in inventory_transactions:
            if (inventory_transaction.getQuantityRemaining()):
                inventory_transaction_list.append(inventory_transaction)

        if (len(inventory_transaction_list) == 0):
            if (self.getLatestSalePrice()):
                return getMoneyString(self.getLatestSalePrice(), include_sign=False)
            else:
                return 'N/A'
        elif (len(inventory_transaction_list) == 1):
            return getMoneyString(inventory_transaction_list[0].sale_price, include_sign=False)
        else:
            sale_price_from = inventory_transaction_list[0].sale_price
            sale_price_to = inventory_transaction_list[-1].sale_price
            if (sale_price_from != sale_price_to):
                return '%s - %s' % (getMoneyString(sale_price_from, include_sign=False),
                                    getMoneyString(sale_price_to, include_sign=False))
            else:
                return getMoneyString(sale_price_from, include_sign=False)

    def getLatestSalePrice(self):
        inventory_transactions = InventoryTransaction.get_all().filter(inventory=self).order_by('-timestamp')
        if len(inventory_transactions):
            return inventory_transactions[0].sale_price
        else:
            return None

    def getDropdownName(self):
        return "%s (%i in stock)" % (self.name, self.getQuantityRemaining())


class InventoryTransaction(LookupModel):
    """Defines the Django model for Inventory Transactions"""
    inventory = models.ForeignKey(Inventory)
    user = models.ForeignKey(User)
    quantity = models.IntegerField()
    cost = models.IntegerField()
    sale_price = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, null=True)

    @staticmethod
    def getActiveTransactions():
        """Returns transactions that have remaining stock"""
        # TODO Add ability to filter un-started transactions
        all_transactions = InventoryTransaction.get_all()
        transactions = []
        for transaction in all_transactions:
            if transaction.getQuantityRemaining():
                transactions.append(transaction)
        return transactions

    def get_dep_duration(self):
        transactions = list(self.transaction_set.order_by('-timestamp'))
        if len(transactions) < 2:
            return None

        day_difference = (transactions[0].timestamp - transactions[-1].timestamp).days
        if day_difference:
            return (len(transactions) / float(day_difference))
        else:
            return 0

    def get_burn_rate(self):
        date = self.timestamp
        average_time_mins = 0
        itx = 0
        for transaction in Transaction.get_all().filter(inventory_transaction=self).order_by('timestamp'):
            itx += 1
            average_time_mins += ((transaction.timestamp - date).total_seconds() / 60.0)
            date = transaction.timestamp
        if itx:
            return (float(average_time_mins) / itx)
        else:
            return None

    def getQuantitySold(self):
        """Returns the number of items sold, based on the number of
           transactions"""
        return len(Transaction.get_all().filter(inventory_transaction=self))

    def getQuantityRemaining(self):
        """Returns the quantity available to purchase from the
           inventory transaction"""
        # Determine the number of items reamining, by removing the number of transactions
        # from the original amount available
        return (self.quantity - self.getQuantitySold())

    def toTimeString(self):
        """Converts the timestamp to a human-readable string"""
        if (self.timestamp.date() == datetime.datetime.today().date()):
            return self.timestamp.strftime("%H:%M")
        else:
            return self.timestamp.strftime("%d/%m/%y %H:%M")

    class Meta:
        """Update the default ordering to reverse timestamp"""
        ordering = ['-timestamp']

    def __str__(self):
        """By default, dispaly the object as the time string"""
        return self.toTimeString()

    def getDescriptiveTitle(self):
        return "%s x %s @ %s" % (self.inventory.name, self.quantity, self.getCostString())

    def getCostString(self):
        """Get the cost as a human-readable string"""
        return getMoneyString(self.cost, include_sign=False)

    def getSalePriceString(self):
        """Get the cost as a human-readable string"""
        return getMoneyString(self.sale_price, include_sign=False)

    def getStockPayments(self):
        return StockPayment.get_all().filter(inventory_transaction=self)

    def getAmountPaid(self):
        return self.getStockPayments().aggregate(models.Sum('amount'))['amount__sum'] or 0

    def getRemainingCost(self):
        return (self.cost - self.getAmountPaid())

    def getCostRemainingString(self):
        return getMoneyString(self.getRemainingCost(), include_sign=False)

    @DbTransaction.atomic
    def updateSalePrice(self, new_sale_price):
        if self.getQuantitySold():
            # If any of the items have been sold, create a new transaction for the
            # items remaining
            remaining_quantity = self.getQuantityRemaining()
            self.quantity -= remaining_quantity
            self.save()

            # Create a new inventory transaction for the new item
            new_inventory_transaction = InventoryTransaction.get_all().get(pk=self.pk)
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
            new_inventory_transaction.timestamp = self.timestamp
            new_inventory_transaction.save()
        else:
            # Else Simply update the transaction
            self.sale_price = new_sale_price
            self.save()


class Transaction(LookupModel):
    user = models.ForeignKey(User, related_name='transaction_user')
    amount = models.IntegerField()
    debit = models.BooleanField(default=True)
    inventory_transaction = models.ForeignKey(InventoryTransaction, null=True)
    payment_type = models.IntegerField()
    description = models.CharField(max_length=255, null=True)
    author = models.ForeignKey(User, related_name='transaction_author')
    affect_float = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class TransactionType(Enum):
        """Types of payment"""
        ITEM_PURCHASE = 1
        CUSTOM_PAYMENT = 2
        ADMIN_CHANGE = 3


    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.toTimeString()

    def getAmountString(self):
        return getMoneyString(self.getAdditionValue())

    def getAdditionValue(self):
        if (self.debit):
            return (0 - self.amount)
        else:
            return self.amount

    def getCurrentCredit(self):
        credit = 0
        transactions = self.user.getTransactionHistory(date_to=self.timestamp)
        for transaction in transactions:
            credit += transaction.getAdditionValue()
        credit += self.getAdditionValue()
        return credit

    def getCurrentCreditString(self):
        return getMoneyString(self.getCurrentCredit())

    def toTimeString(self):
        if (self.timestamp.date() == datetime.datetime.today().date()):
            return self.timestamp.strftime("%H:%M")
        else:
            return self.timestamp.strftime("%d/%m/%y %H:%M")

class StockPaymentTransaction(LookupModel):
    author = models.ForeignKey(User, related_name='author')
    user = models.ForeignKey(User, related_name='user')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def toTimeString(self):
        if self.timestamp.date() == datetime.datetime.today().date():
            return self.timestamp.strftime("%H:%M")
        else:
            return self.timestamp.strftime("%d/%m/%y %H:%M")

    def getAmountString(self):
        return getMoneyString(self.getAmount(), include_sign=False)

    def getStockPayments(self):
        return StockPayment.get_all().filter(stock_payment_transaction=self)

    def getAmount(self):
        amount = 0
        for stock_payment in self.getStockPayments():
            amount += stock_payment.amount
        return amount

class StockPayment(LookupModel):
    user = models.ForeignKey(User)
    inventory_transaction = models.ForeignKey(InventoryTransaction, null=True)
    stock_payment_transaction = models.ForeignKey(StockPaymentTransaction)
    amount = models.IntegerField()
    description = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def toTimeString(self):
        if (self.timestamp.date() == datetime.datetime.today().date()):
            return self.timestamp.strftime("%H:%M")
        else:
            return self.timestamp.strftime("%d/%m/%y %H:%M")

    def getAmountString(self):
        return getMoneyString(self.amount, include_sign=False)

    def getNotes(self):
        if not self.inventory_transaction:
            return '(Will be used during next stock payment)'

        if self.inventory_transaction.getRemainingCost():
            notes = 'Partially paid'
        else:
            notes = 'Fully paid'

        if (len(self.inventory_transaction.getStockPayments()) > 1 or
                self.inventory_transaction.getRemainingCost()):
            notes += ' (in installments)'

        return notes


class Token(LookupModel):
    user = models.ForeignKey(User)
    token_value = models.CharField(max_length=100)

class Change(LookupModel):
    timestamp = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=255)
    object_id = models.IntegerField()
    user = models.ForeignKey(User)
    changed_field = models.CharField(max_length=255)
    previous_value = models.CharField(max_length=255)
    new_value = models.CharField(max_length=255)
