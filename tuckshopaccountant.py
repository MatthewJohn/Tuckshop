#!/usr/bin/python

import sqlite3
import os

import ldap

import BaseHTTPServer
import jinja2

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

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

class Auth(object):
  def login(request, username, password):
    ldap_obj = ldap.initialize('ldap://ldap-server:389')
    dn = 'uid=%s,ou=People,dc=example,dc=com' % username
    try:
      ldap_obj.simple_bind_s(dn, password)
    except:
      return False
    return User(username)

  def logout(request):
    pass

class User(object):
  def __init__(self, username):
    self.username = username

    # Obtain information from LDAP
    ldap_obj = ldap.initialize('ldap://ldap-server:389')
    dn = 'uid=%s,ou=People,dc=example,dc=com' % username
    ldap_obj.simple_bind_s()
    res = ldap_obj.search_s('ou=People,dc=example,dc=com', ldap.SCOPE_ONELEVEL,
                            'uid=%s' % username, ['mail', 'displayName'])

    if (not res):
      raise Exception('User \'%s\' does not exist' % username)

    self.dn = res[0][0]
    self.display_name = res[0][1]['displayName']
    self.email = res[0][1]['mail']

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

  def getCredit(self):
    credit = sql_c.execute('''SELECT credit FROM credit WHERE uid=?''', (self.getUsername(), )).fetchone()
    return credit[0]

  def addCredit(self, amount):
    amount = float("%.2f" % amount)
    sql_c.execute('''INSERT INTO purchase_history(inventory_id, uid, amount, debit) VALUES(0, ?, ?, ?)''', (self.getUsername(), amount, False))
    credit = self.getCredit() + amount
    sql_c.execute('''UPDATE credit SET credit=? WHERE uid=?''', (credit, self.getUsername()))
    sql_conn.commit()
    return self.getCredit()

  def removeCredit(self, amount):
    amount = float("%.2f" % amount)
    sql_c.execute('''INSERT INTO purchase_history(inventory_id, uid, amount, debit) VALUES(0, ?, ?, ?)''', (self.getUsername(), amount, True))
    credit = self.getCredit() - amount
    sql_c.execute('''UPDATE credit SET credit=? WHERE uid=?''', (credit, self.getUsername()))
    sql_conn.commit()
    return self.getCredit()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  sessions = {}

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

  def do_GET(self):
      # Get file
      split_path = self.path.split('/')
      base_dir = split_path[1] if (len(split_path) > 1) else ''
      file_name = split_path[2] if len(split_path) == 3 else ''

      if (base_dir == 'css'):
        self.getFile('text/css', 'css', file_name)
      elif (base_dir == 'js'):
        self.getFile('text/javascript', 'js', file_name)

      elif (base_dir == '' or base_dir == 'credit'):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        user = User()
        template = env.get_template('credit.html')
        self.wfile.write(template.render(page_name='Credit', user=user))

      else:
        self.end_headers()
        self.wfile.write('help me!!%s' % self.path)
      return

  def do_POST(self):
    # Get file
    split_path = self.path.split('/')
    base_dir = split_path[1] if (len(split_path) > 1) else ''
    file_name = split_path[2] if len(split_path) == 3 else ''

    self.do_GET()
    return

if (__name__ == '__main__'):

  server_address = ('', 8000)
  httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
  httpd.serve_forever()
