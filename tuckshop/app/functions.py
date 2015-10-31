from config import LDAP_SERVER

def getMoneyString(credit):
  text_color = 'green' if credit >= 0 else 'red'

  if (credit <= -1):
    credit_sign = '-'
    credit = 0 - credit
  else:
    credit_sign = ''

  if (credit < 1):
    credit_string = str(int(credit * 100)) + 'p'
  else:
    credit_string = '&pound;%.2f' % credit

  return '<font style="color: %s">%s%s</font>' % (text_color, credit_sign, credit_string)


def login(username, password):
  import ldap
  from models import User
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