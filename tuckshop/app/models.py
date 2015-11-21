from django.db import models

from config import LDAP_SERVER
from functions import getMoneyString
import ldap
from decimal import Decimal
import datetime

# Create your models here.
class User(models.Model):
  uid = models.CharField(max_length=10)
  credit = models.IntegerField(default=0)
  admin = models.BooleanField(default=False)

  def __init__(self, *args, **kwargs):

    user_object = super(User, self).__init__(*args, **kwargs)

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

  def addCredit(self, amount):
    amount = int(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    self.credit += amount
    self.save()
    return self.credit

  def removeCredit(self, amount=None, inventory=None):
    if (inventory and inventory.quantity <= 0):
      raise Exception('There are no items in stock')

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

    self.credit -= amount
    self.save()

    return self.credit

  def getCreditString(self):
    return getMoneyString(self.credit)

  def getTransactionHistory(self, date_from=None, date_to=None):
    if date_from is None:
      date_from = datetime.datetime.fromtimestamp(0)

    if date_to is None:
      date_to = datetime.datetime.now()
    return Transaction.objects.filter(user=self, timestamp__gte=date_from, timestamp__lte=date_to)


class Inventory(models.Model):
  name = models.CharField(max_length=200)
  bardcode_number = models.CharField(max_length=25, null=True)
  price = models.IntegerField()
  image_url = models.CharField(max_length=250, null=True)
  quantity = models.IntegerField(default=0)
  archive = models.BooleanField(default=False)

  @staticmethod
  def getAvailableItems():
    return Inventory.objects.filter(quantity__gt=0).filter(archive=False)

  def getSalePriceString(self):
    return getMoneyString(self.price, include_sign=False)

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

class Transaction(models.Model):
  user = models.ForeignKey(User)
  amount = models.IntegerField()
  debit = models.BooleanField(default=True)
  inventory = models.ForeignKey(Inventory, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-timestamp']

  def __str__(self):
    return self.toTimeString()

  def getAmountString(self):
    return getMoneyString(self.amount)

  def getAdditionValue(self):
    if (self.debit):
      return (0 - self.amount)
    else:
      return self.amount

  def getCurrentCredit(self):
    credit = 0
    for transaction in Transaction.objects.filter(user=self.user, pk__lt=self.id):
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