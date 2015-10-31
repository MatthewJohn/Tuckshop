from django.db import models

from config import LDAP_SERVER
from functions import getMoneyString
import ldap
from decimal import Decimal
import datetime

# Create your models here.
class User(models.Model):
  uid = models.CharField(max_length=10)
  credit = models.DecimalField(max_digits=5, decimal_places=2, default=0)
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
    amount = Decimal(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    self.credit += amount
    self.save()
    return self.credit

  def removeCredit(self, amount=None, inventory=None):
    transaction = Transaction(user=self, debit=True)

    if (inventory):
      transaction.inventory = inventory
      if (not amount):
        amount = inventory.sale_price

    elif not amount:
      raise Exception('Must pass amount or inventory')

    amount = Decimal(amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')

    transaction.amount = amount
    transaction.save()

    self.credit -= amount
    self.save()

    return self.credit

  def getCreditString(self):
    return getMoneyString(self.credit)

  def getTransactionHistory(self, date_from=datetime.datetime.fromtimestamp(0),
                            date_to=datetime.datetime.now()):

    return Transaction.objects.filter(user=self, timestamp__gt=date_from, timestamp__lt=date_to)


class Inventory(models.Model):
  name = models.CharField(max_length=200)
  bardcode_number = models.CharField(max_length=25, null=True)
  cost = models.DecimalField(max_digits=4, decimal_places=2)
  sale_price = models.DecimalField(max_digits=4, decimal_places=2)
  image_url = models.CharField(max_length=250, null=True)

class Transaction(models.Model):
  user = models.ForeignKey(User)
  amount = models.DecimalField(max_digits=5, decimal_places=2)
  debit = models.BooleanField(default=True)
  inventory = models.ForeignKey(Inventory, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  def getAdditionValue(self):
    if (self.debit):
      return (0 - self.amount)
    else:
      return self.amount

  def getCurrentCredit(self, user):
    credit = 0
    for transaction in Transaction.objects.filter(user=user, timestamp__lte=self.timestamp):
      credit += transaction.getAdditionValue()
    credit += self.getAdditionValue()
    return credit

class Token(models.Model):
  user = models.ForeignKey(User)
  token_value = models.CharField(max_length=100)