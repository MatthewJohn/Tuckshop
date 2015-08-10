#!/usr/bin/python

import sqlite3
import os

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
             (id INTEGER PRIMARY KEY AUTOINCREMENT, bardcode_number text, uid text, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
  sql_cursor.execute('''CREATE TABLE admin
             (uid text)''')
  sql_connection.commit()

database_exists = (os.path.isfile(SQL_FILE))

sql_conn = sqlite3.connect(SQL_FILE)

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

import BaseHTTPServer
import jinja2

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

env = Environment()
env.loader = FileSystemLoader('./templates/')

class User(object):
  def __init__(self, username='mc'):
    self.username = username

  def getName(self):
    return 'Lloyd'

  def getCredit(self):
    return 135

  def addCredit(self, amount):
    return 135 + amount

  def removeCredit(self, amount):
    return 135 - amount

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

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


server_address = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
httpd.serve_forever()
