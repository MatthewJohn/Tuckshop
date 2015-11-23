from config import LDAP_SERVER
from os import environ

def getMoneyString(credit, include_sign=True):
  text_color = 'green' if credit >= 0 else 'red'

  if (credit < 0):
    credit_sign = '-'
    credit = 0 - credit
  else:
    credit_sign = ''

  if (credit < 100):
    credit_string = str(credit) + 'p'
  else:
    credit_string = '&pound;%.2f' % (float(credit) / 100)

  if (include_sign):
    return '<font style="color: %s">%s%s</font>' % (text_color, credit_sign, credit_string)
  else:
    return credit_string


def login(username, password):
  import ldap
  from models import User
  if not ('TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']):
    ldap_obj = ldap.initialize('ldap://%s:389' % LDAP_SERVER)
    dn = 'uid=%s,ou=People,dc=example,dc=com' % username
    try:
      ldap_obj.simple_bind_s(dn, password)
    except:
      return False

  user_object = User.objects.filter(uid=username)
  if (not len(user_object)):
    user_object = User(uid=username)
    user_object.save()
  else:
    user_object = user_object[0]

  return user_object