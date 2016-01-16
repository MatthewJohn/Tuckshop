from django.db import models

from config import LDAP_SERVER, SHOW_OUT_OF_STOCK_ITEMS
from tuckshop.app.redis_connection import RedisConnection
from functions import getMoneyString
import ldap
from decimal import Decimal
import datetime
from os import environ

# Create your models here.
class User(models.Model):
  uid = models.CharField(max_length=10)
  admin = models.BooleanField(default=False)

  current_credit_cache_key = 'User_%s_credit'

  def __init__(self, *args, **kwargs):

    user_object = super(User, self).__init__(*args, **kwargs)

    if not ('TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']):
      # Obtain information from LDAP
      ldap_obj = ldap.initialize('ldap://%s:389' % LDAP_SERVER)
      dn = 'uid=%s,ou=People,dc=example,dc=com' % self.uid
      ldap_obj.simple_bind_s()
      res = ldap_obj.search_s('ou=People,dc=example,dc=com', ldap.SCOPE_ONELEVEL,
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

  def payForStock(self, amount, pay_to_credit=False):
    if amount < 0:
      raise Exception('Amount must be a positive')

    semi_paid_transaction = None
    for transaction in self.getUnpaidTransactions():
      partial_payment = bool(transaction.getAmountPaid())
      transaction_amount = 0
      if transaction.getRemainingCost() > amount:
        transaction_amount = amount
        semi_paid_transaction = transaction
        fully_paid = False
      else:
        transaction_amount = transaction.getRemainingCost()
        fully_paid = True

      StockPayment(user=self, inventory_transaction=transaction, amount=transaction_amount,
                   fully_paid=fully_paid, installment=bool(transaction.cost - transaction_amount)).save()
      transaction.save()

      amount -= transaction_amount
      if amount == 0:
        break

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
    for inventory_transaction in InventoryTransaction.objects.filter(user=self):
      if inventory_transaction.getRemainingCost():
        inventory_transactions.append(inventory_transaction)
    inventory_transactions.sort(key=lambda x: (-x.getAmountPaid(), bool(x.getQuantityRemaining()), x.timestamp))
    return inventory_transactions

  def getCurrentCredit(self, refresh_cache=False):
    if (refresh_cache or
        not RedisConnection.exists(User.current_credit_cache_key % self.id)):
      balance = 0
      for transaction in Transaction.objects.filter(user=self):
        if (transaction.debit):
          balance -= transaction.amount
        else:
          balance += transaction.amount

      # Update cache
      RedisConnection.set(User.current_credit_cache_key % self.id, balance)
    else:
      # Obtain credit from cache
      balance = RedisConnection.get(User.current_credit_cache_key % self.id)
    return balance

  def addCredit(self, amount, description=None):
    amount = int(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    current_credit = self.getCurrentCredit()
    transaction = Transaction(user=self, amount=amount, debit=False, description=description)
    transaction.save()

    # Update credit cache
    current_credit += amount
    RedisConnection.set(User.current_credit_cache_key % self.id,
                        current_credit)
    return current_credit

  def removeCredit(self, amount=None, inventory=None, description=None):
    if (inventory and inventory.getQuantityRemaining() <= 0):
      raise Exception('There are no items in stock')

    current_credit = self.getCurrentCredit()
    transaction = Transaction(user=self, debit=True)

    if (inventory):
      inventory_transaction = inventory.getCurrentInventoryTransaction()
      if inventory_transaction is None:
        raise Exception('No inventory transaction available for this item')

      transaction.inventory_transaction = inventory_transaction

      if (not amount):
        amount = inventory_transaction.sale_price

    elif not amount:
      raise Exception('Must pass amount or inventory')

    amount = int(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')

    transaction.amount = amount
    transaction.description = description
    transaction.save()

    # Update credit cache
    current_credit -= amount
    RedisConnection.set(User.current_credit_cache_key % self.id,
                        current_credit)

    return current_credit

  def getCreditString(self):
    return getMoneyString(self.getCurrentCredit())

  def getTransactionHistory(self, date_from=None, date_to=None):
    if date_from is None:
      date_from = datetime.datetime.fromtimestamp(0)

    if date_to is None:
      date_to = datetime.datetime.now()

    return Transaction.objects.filter(user=self, timestamp__gt=date_from, timestamp__lt=date_to)

  def getStockPayments(self):
    return StockPayment.objects.filter(user=self)


class Inventory(models.Model):
  name = models.CharField(max_length=200)
  bardcode_number = models.CharField(max_length=25, null=True)
  image_url = models.CharField(max_length=250, null=True)
  archive = models.BooleanField(default=False)

  inventory_transaction_cache_key = 'Inventory_%s_inventory_transaction'

  def getSalePrice(self):
    if self.getCurrentInventoryTransaction():
      return self.getCurrentInventoryTransaction().sale_price
    else:
      return None

  def getQuantityRemaining(self, include_all_transactions=True):
    if (include_all_transactions):
      quantity = 0
      for transaction in InventoryTransaction.objects.filter(inventory=self):
        quantity += transaction.getQuantityRemaining()
    else:
      quantity = self.getCurrentInventoryTransaction().getQuantityRemaining()
    return quantity


  def getCurrentInventoryTransaction(self, refresh_cache=False):
    cache_key = Inventory.inventory_transaction_cache_key % self.id
    cache_exists = RedisConnection.exists(cache_key)

    # If the cache if to be refreshed or the cache has not been set,
    # calculate the current inventory transaction for the item
    if (refresh_cache or not cache_exists):

      # Iterate through the inventory transactions for this item
      for transaction in InventoryTransaction.objects.filter(inventory=self).order_by('-timestamp'):

        # If the transaction has items left, set this as the current
        # transaction and return it
        if (transaction.getQuantityRemaining()):
          RedisConnection.set(cache_key, transaction.id)
          return transaction

      # If no active transaction were found, clear the cache and
      # return with None
      if cache_exists:
        RedisConnection.delete(cache_key)
      return None
    else:
      transaction = InventoryTransaction.objects.get(pk=RedisConnection.get(cache_key))

      # Ensure that the transaction has items left
      if (transaction.getQuantityRemaining()):
        # If so, return the transaction
        return transaction
      else:
        # Otherwise, clear the cache and use this function to search for a new
        # transaction
        return self.getCurrentInventoryTransaction(refresh_cache=True)

  def getImageUrl(self):
    # Return the image URL, if it exists. Else, return a default image
    return self.image_url if self.image_url else 'http://www.monibazar.com/images/noimage.png'

  @staticmethod
  def getAvailableItems():
    items = Inventory.objects.filter(archive=False)
    if not SHOW_OUT_OF_STOCK_ITEMS:
      for item in items:
        if (not item.getCurrentInventoryTransaction().getQuantityRemaining()):
          items.remove(item)

    return items

  def getSalePriceString(self):
    # Attempt to get the price from the current transaction
    price = self.getSalePrice()

    if price is None:
      # If there is no current transaction, return the price
      # from the last transaction
      transactions = InventoryTransaction.objects.filter(inventory=self).order_by('-timestamp')
      if len(transactions):
        return  getMoneyString(transactions[0].sale_price, include_sign=False)
      else:
        return 'N/A'

    else:
      return getMoneyString(price, include_sign=False)

  def getPriceRangeString(self):
    inventory_transactions = InventoryTransaction.objects.filter(inventory=self).order_by('sale_price')
    inventory_transaction_list = []
    for inventory_transaction in inventory_transactions:
      if (inventory_transaction.getQuantityRemaining()):
        inventory_transaction_list.append(inventory_transaction)

    if (len(inventory_transaction_list) == 0):
      if (self.getLatestSalePrice()):
        return self.getLatestSalePrice()
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
    inventory_transactions = InventoryTransaction.objects.filter(inventory=self).order_by('-timestamp')
    if len(inventory_transactions):
      return inventory_transactions[0].sale_price
    else:
      return None

  def getDropdownName(self):
    return "%s (%i in stock)" % (self.name, self.getQuantityRemaining())


class InventoryTransaction(models.Model):
  """Defines the Django model for Inventory Transactions"""
  inventory = models.ForeignKey(Inventory)
  user = models.ForeignKey(User)
  quantity = models.IntegerField()
  cost = models.IntegerField()
  sale_price = models.IntegerField()
  timestamp = models.DateTimeField(auto_now_add=True)
  description = models.CharField(max_length=255, null=True)

  def getQuantityRemaining(self):
    """Returns the quantity available to purchase from the
       inventory transaction"""
    # Determine the number of items reamining, by removing the number of transactions
    # from the original amount available
    transactions = Transaction.objects.filter(inventory_transaction=self)
    return (self.quantity - len(transactions))

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

  def getAmountPaid(self):
    return StockPayment.objects.filter(inventory_transaction=self).aggregate(models.Sum('amount'))['amount__sum'] or 0

  def getRemainingCost(self):
    return (self.cost - self.getAmountPaid())

  def getCostRemainingString(self):
    return getMoneyString(self.getRemainingCost(), include_sign=False)


class Transaction(models.Model):
  user = models.ForeignKey(User)
  amount = models.IntegerField()
  debit = models.BooleanField(default=True)
  inventory_transaction = models.ForeignKey(InventoryTransaction, null=True)
  description = models.CharField(max_length=255, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

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


class StockPayment(models.Model):
  user = models.ForeignKey(User)
  inventory_transaction = models.ForeignKey(InventoryTransaction)
  amount = models.IntegerField()
  fully_paid = models.BooleanField(default=False)
  installment = models.BooleanField(default=False)
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
    if self.fully_paid:
      notes = 'Fully paid'
    else:
      notes = 'Partially paid'

    if self.installment:
      notes += ' (in installments)'

    return notes


class Token(models.Model):
  user = models.ForeignKey(User)
  token_value = models.CharField(max_length=100)