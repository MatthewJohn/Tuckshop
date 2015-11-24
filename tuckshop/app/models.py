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
  credit = models.IntegerField(default=0)
  admin = models.BooleanField(default=False)

  current_credit_cache_key = 'User_%s_credit'

  def __init__(self, *args, **kwargs):

    user_object = super(User, self).__init__(*args, **kwargs)

    if not ('TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']):
      # Obtain information from LDAP
      ldap_obj = ldap.initialize('ldap://%s:389' % LDAP_SERVER)
      dn = 'uid=%s,o=I.T. Dev Ltd,ou=People,dc=itdev,dc=co,dc=uk' % self.uid
      ldap_obj.simple_bind_s()
      res = ldap_obj.search_s('o=I.T. Dev Ltd,ou=People,dc=itdev,dc=co,dc=uk', ldap.SCOPE_ONELEVEL,
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

  def payForStock(self, amount):
    pass

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


  def addCredit(self, amount):
    amount = int(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    current_credit = self.getCurrentCredit()
    transaction = Transaction(user=self, amount=amount, debit=False)
    transaction.save()

    # Update credit cache
    current_credit += amount
    RedisConnection.set(User.current_credit_cache_key % self.id,
                        current_credit)
    return current_credit

  def removeCredit(self, amount=None, inventory=None):
    if (inventory and inventory.quantity <= 0):
      raise Exception('There are no items in stock')

    current_credit = self.getCurrentCredit()
    transaction = Transaction(user=self, debit=True)

    if (inventory):
      transaction.inventory = inventory

      if (not amount):
        amount = inventory.price

    elif not amount:
      raise Exception('Must pass amount or inventory')

    amount = int(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')

    transaction.amount = amount
    transaction.save()

    if (inventory):
      inventory.quantity -= 1
      inventory.save()

    # Update credit cache
    current_credit -= amount
    RedisConnection.set(User.current_credit_cache_key % self.id,
                        current_credit)

    return current_credit

  def getCreditString(self):
    return getMoneyString(self.getCurrentCredit())

  def getTransactionHistory(self, date_from=None, date_to=None,
                            include_inventory_history=False):
    if date_from is None:
      date_from = datetime.datetime.fromtimestamp(0)

    if date_to is None:
      date_to = datetime.datetime.now()

    return Transaction.objects.filter(user=self, timestamp__gt=date_from, timestamp__lt=date_to)


class Inventory(models.Model):
  name = models.CharField(max_length=200)
  bardcode_number = models.CharField(max_length=25, null=True)
  image_url = models.CharField(max_length=250, null=True)
  quantity = models.IntegerField(default=0)
  archive = models.BooleanField(default=False)

  current_price_cache_key = 'Inventory_%s_price'

  def getCurrentPrice(self, refresh_cache=False):
    if (not RedisConnection.exists(Inventory.current_price_cache_key % self.id) or refresh_cache):
      current_price = self.getCurrentInventoryTransaction().sale_price
      RedisConnection.set(Inventory.current_price_cache_key % self.id, current_price)
      return current_price
    else:
      return RedisConnection.get(Inventory.current_price_cache_key % self.id)

  def getCurrentInventoryTransaction(self, refresh_cache=False):
    pass

  def getImageUrl(self):
    return self.image_url if self.image_url else 'http://www.onlineseowebservice.com/news/wp-content/themes/creativemag/images/default.png'

  @staticmethod
  def getAvailableItems():
    items = Inventory.objects.filter(archive=False)
    if not SHOW_OUT_OF_STOCK_ITEMS:
      items = items.filter(quantity__gt=0)

    return items

  def getSalePriceString(self):
    return getMoneyString(self.getCurrentPrice(), include_sign=False)

  def addItems(self, quantity, user, cost):
    transaction = InventoryTransaction(inventory=self, user=user, quantity=quantity, cost=cost)
    transaction.save()

    self.quantity += quantity
    self.save()

  def getDropdownName(self):
    return "%s (%i in stock)" % (self.name, self.quantity)


class InventoryTransaction(models.Model):
  inventory = models.ForeignKey(Inventory)
  user = models.ForeignKey(User)
  quantity = models.IntegerField()
  cost = models.IntegerField()
  sale_price = models.IntegerField()
  approved = models.BooleanField(default=False)
  timestamp = models.DateTimeField(auto_now_add=True)

  def toTimeString(self):
    if (self.timestamp.date() == datetime.datetime.today().date()):
      return self.timestamp.strftime("%H:%M")
    else:
      return self.timestamp.strftime("%d/%m/%y %H:%M")

  def approve(self):
    self.approved = True
    self.save()
    self.user.credit += self.cost
    self.user.save()

  class Meta:
    ordering = ['-timestamp']

  def __str__(self):
    return self.toTimeString()

  def getAmountString(self):
    return getMoneyString(self.cost)

  def getAdditionValue(self):
     return self.cost

  def getCurrentCreditString(self):
    return getMoneyString(self.getCurrentCredit())

class Transaction(models.Model):
  user = models.ForeignKey(User)
  amount = models.IntegerField()
  debit = models.BooleanField(default=True)
  inventory_transactions = models.ForeignKey(InventoryTransaction, null=True)
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

class Token(models.Model):
  user = models.ForeignKey(User)
  token_value = models.CharField(max_length=100)