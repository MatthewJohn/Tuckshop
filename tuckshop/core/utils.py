from os import environ
import ldap


def getMoneyString(credit, include_sign=True, colour_switch=False):
    positive_colour = 'green' if not colour_switch else 'red'
    negative_colour = 'red' if not colour_switch else 'green'
    text_color = positive_colour if credit >= 0 else negative_colour

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
    from tuckshop.core.config import LDAP_SERVER
    from tuckshop.app.models import User
    if 'TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']:
        # If tuckshop in development mode, match all passwords
        # again 'password'
        if password != 'password':
            return False
    else:
        # Otherwise authenticate against LDAP server
        ldap_obj = ldap.initialize('ldap://%s:389' % LDAP_SERVER)
        dn = 'uid=%s,ou=People,dc=example,dc=com' % username
        try:
            # Attempt to bind to LDAP
            ldap_obj.simple_bind_s(dn, password)
        except:
            # If the connection throws an exception, return False
            return False

    # Create user object for currently logged in user
    user_object = User.objects.filter(uid=username)

    # If a user object does not exist, create a new one
    if (not len(user_object)):
        user_object = User(uid=username)
        user_object.save()
    else:
        user_object = user_object[0]

    # Return user object
    return user_object