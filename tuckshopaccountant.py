#!/usr/bin/python

import sqlite3
import os

import ldap

import BaseHTTPServer
import jinja2

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

import cgi

import Cookie
import datetime
import random
import sha
import time

SQL_FILE = 'tuckshopaccountant.db'

def create_schema(sql_connection):
  sql_cursor = sql_connection.cursor()
  sql_cursor.execute('''CREATE TABLE credit
             (uid text PRIMARY KEY, credit real)''')
  sql_cursor.execute('''CREATE TABLE token
             (uid text, token text)''')
  sql_cursor.execute('''CREATE TABLE inventory
             (id INTEGER PRIMARY KEY AUTOINCREMENT, bardcode_number text, cost real)''')
  sql_cursor.execute('''CREATE TABLE purchase_history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, inventory_id integer, uid text, amount real, debit boolean DEFAULT TRUE, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
  sql_cursor.execute('''CREATE TABLE admin
             (uid text)''')
  sql_connection.commit()

database_exists = (os.path.isfile(SQL_FILE))

sql_conn = sqlite3.connect(SQL_FILE, isolation_level='IMMEDIATE')

if (not database_exists):
  create_schema(sql_conn)

sql_c = sql_conn.cursor()


# Setup listener for RDIF to obtain login details
# from asyncore import file_dispatcher, loop
# from evdev import InputDevice, categorize, ecodes
# dev = InputDevice('/dev/input/event8')

# class InputDeviceDispatcher(file_dispatcher):
#   def __init__(self, device):
#     self.device = device
#     file_dispatcher.__init__(self, device)

#   def recv(self, ign=None):
#     return self.device.read()

#   def handle_read(self):
#     for event in self.recv():
#       print(repr(event))

#InputDeviceDispatcher(dev)
#loop()

env = Environment()
env.loader = FileSystemLoader('./templates/')

sessions = {}

class Auth(object):
  def __init__(self, username, password):
    self.login(username, password)
    self.username = username

  @staticmethod
  def login(username, password):

    ldap_obj = ldap.initialize('ldap://localhost:389')
    dn = 'uid=%s,ou=People,dc=example,dc=com' % username
    try:
      ldap_obj.simple_bind_s(dn, password)
    except:
      return False
    return True

  def getUsername(self):
    return self.username

  def isAdmin(self):
    admin_count = sql_c.execute('''SELECT count(*) FROM admin WHERE uid=?''', (self.getUsername(), ))
    admin_count = user_count.fetchone()[0]
    if (admin_count):
      return True
    else:
      return False


class User(object):
  def __init__(self, username):
    self.username = username

    # Obtain information from LDAP
    ldap_obj = ldap.initialize('ldap://localhost:389')
    dn = 'uid=%s,ou=People,dc=example,dc=com' % username
    ldap_obj.simple_bind_s()
    res = ldap_obj.search_s('ou=People,dc=example,dc=com', ldap.SCOPE_ONELEVEL,
                            'uid=%s' % username, ['mail', 'givenName'])

    if (not res):
      raise Exception('User \'%s\' does not exist' % username)

    self.dn = res[0][0]
    self.display_name = res[0][1]['givenName'][0]
    self.email = res[0][1]['mail'][0]

    # Determine if user exists in user table and create if not
    user_count = sql_c.execute('''SELECT count(*) FROM credit WHERE uid=?''', (self.getUsername(), ))
    user_count = user_count.fetchone()[0]
    if (not user_count):
      sql_c.execute('INSERT INTO credit(uid, credit) VALUES(?, 0.00)', (self.getUsername(), ))
      sql_conn.commit()

  @staticmethod
  def getCurrentUser(request):
    return User(Auth.getCurrentUser(request))

  def getName(self):
    return self.display_name

  def getUsername(self):
    return self.username

  def getEmail(self):
    return self.email

  def getCredit(self):
    credit = sql_c.execute('''SELECT credit FROM credit WHERE uid=?''', (self.getUsername(), )).fetchone()
    return credit[0]

  def getCreditString(self):
    credit = self.getCredit()
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

  def addCredit(self, amount):
    amount = float("%.2f" % amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    sql_c.execute('''INSERT INTO purchase_history(inventory_id, uid, amount, debit) VALUES(0, ?, ?, ?)''', (self.getUsername(), amount, False))
    credit = self.getCredit() + amount
    sql_c.execute('''UPDATE credit SET credit=? WHERE uid=?''', (credit, self.getUsername()))
    sql_conn.commit()
    return self.getCredit()

  def removeCredit(self, amount):
    amount = float("%.2f" % amount)
    if (amount < 0):
      raise Exception('Cannot use negative number')
    sql_c.execute('''INSERT INTO purchase_history(inventory_id, uid, amount, debit) VALUES(0, ?, ?, ?)''', (self.getUsername(), amount, True))
    credit = self.getCredit() - amount
    sql_c.execute('''UPDATE credit SET credit=? WHERE uid=?''', (credit, self.getUsername()))
    sql_conn.commit()
    return self.getCredit()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def getSession(self, send_header=False, clear_cookie=False):
    cookie = Cookie.SimpleCookie()
    cookie_found = False
    if ('Cookie' in self.headers):
      cookie.load(self.headers.getheader('Cookie'))
      if ('sid' in cookie and cookie['sid']):
        sid = cookie['sid'].value
        cookie_found = True

    if (not cookie_found):
      sid = sha.new(repr(time.time())).hexdigest()
      cookie['sid'] = sid
      cookie['sid']['expires'] = 24 * 60 * 60
      if (send_header):
        self.send_header('Set-Cookie', cookie.output())

    if (sid not in sessions):
      sessions[sid] = {}

    if (clear_cookie):
      del sessions[sid]
      cookie['sid'] = None
      self.send_header('Set-Cookie', cookie.output())

    return sid

  def getSessionVar(self, var):
    session_var = self.getSession()

    if (var in sessions[session_var]):
      return sessions[session_var][var]
    else:
      return None

  def setSessionVar(self, var, value):
    sessions[self.getSession()][var] = value

  def getFile(self, content_type, base_dir, file_name):
    file_name = '%s/%s' % (base_dir, file_name)

    if (file_name and os.path.isfile(file_name)):
      self.send_response(200)
      self.send_header('Content-type', content_type)
      self.end_headers()
      self.wfile.write(self.includeFile(file_name))
    else:
      self.send_response(401)

  def includeFile(self, file_name):
    if (file_name and os.path.isfile(file_name)):
      with open(file_name) as fh:
        return fh.read()
    else:
      return 'Cannot file find!'

  def sendLogin(self):
    template = env.get_template('login.html')
    if ('auth_failure' in self.post_vars and self.post_vars['auth_failure']):
      error = '<div class="alert alert-danger" role="alert">Incorrect Username and/or Password</div>'
    else:
      error = None
    self.wfile.write(template.render(page_name='Login', warning=error))

  def isLoggedIn(self):
    if (self.getSessionVar('username')):
      return True
    else:
      return False

  def getCurrentUsername(self):
    if (self.isLoggedIn()):
      return self.getSessionVar('username')
    else:
      return None

  def getUserObject(self):
    if (self.isLoggedIn()):
      return User(self.getCurrentUsername())

  def getCurrentAuthObject(self):
    if (self.isLoggedIn()):
      return Auth(self.getCurrentUsername(), self.getSessionVar['password'])

  def do_GET(self, post_vars={}):
    # Get file
    self.post_vars = post_vars
    split_path = self.path.split('/')
    base_dir = split_path[1] if (len(split_path) > 1) else ''
    file_name = split_path[2] if len(split_path) == 3 else ''

    if (base_dir == 'css'):
      self.getFile('text/css', 'css', file_name)
    elif (base_dir == 'js'):
      self.getFile('text/javascript', 'js', file_name)

    elif (base_dir == 'logout'):
      self.send_response(200)
      self.getSession(clear_cookie=True)
      self.end_headers()
      self.sendLogin()

    elif (base_dir in ['', 'credit', 'logout']):
      self.getSession()
      if ('set_response' not in post_vars):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
      if (not self.isLoggedIn()):
        self.sendLogin()
      elif (base_dir == '' or base_dir == 'credit'):
        template = env.get_template('credit.html')
        self.wfile.write(template.render(page_name='Credit', user=self.getUserObject()))

    else:
      self.send_response(404)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      self.wfile.write('Unknown URL: %s' % self.path)

    return

  def getPostVariables(self):
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
               'CONTENT_TYPE':self.headers['Content-Type'],
              })
    variables = {}
    for field in form.keys():
      variables[field] = form[field].value
    return variables

  def do_POST(self):
    self.send_response(200)
    self.getSession(True)

    post_vars = {}
    # Get file
    split_path = self.path.split('/')
    base_dir = split_path[1] if (len(split_path) > 1) else ''
    file_name = split_path[2] if len(split_path) == 3 else ''

    variables = self.getPostVariables()

    if ('action' in variables):
      action = variables['action']

      # Handle login POST requests
      if (action == 'login'):
        post_vars['auth_failure'] = True
        if ('password' in variables and 'username' in variables and self.login(variables['username'], variables['password'])):
          post_vars['auth_failure'] = False

      if (action == 'pay' and 'amount' in variables):
        self.getUserObject().removeCredit(float(variables['amount']))

      self.do_GET(post_vars=post_vars)
    return

  def login(self, username, password):
    if (Auth.login(username, password)):
      self.setSessionVar('username', username)
      self.setSessionVar('password', password)
      return True
    else:
      return False

if (__name__ == '__main__'):

  server_address = ('', 8000)
  httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
  httpd.serve_forever()
