#!/usr/bin/python

import sqlite3
import os

SQL_FILE = 'tuckshopaccountant.db'

def create_schema(sql_connection):
  sql_cursor = sql_connection.cursor()
  sql_cursor.execute('''CREATE TABLE credit
             (uid text PRIMARY KEY, credit real, rfid_token text)''')
  sql_cursor.execute('''CREATE TABLE inventory
             (id INTEGER PRIMARY KEY AUTOINCREMENT, bardcode_number text, cost real)''')
  sql_cursor.execute('''CREATE TABLE purchase_history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, bardcode_number text, uid text, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
  sql_connection.commit()

database_exists = (os.path.isfile(SQL_FILE))

sql_conn = sqlite3.connect(SQL_FILE)

if (not database_exists):
  create_schema(sql_conn)

sql_c = sql_conn.cursor()


# Setup listener for RDIF to obtain login details
from asyncore import file_dispatcher, loop
from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event8')

class InputDeviceDispatcher(file_dispatcher):
  def __init__(self, device):
    self.device = device
    file_dispatcher.__init__(self, device)

  def recv(self, ign=None):
    return self.device.read()

  def handle_read(self):
    for event in self.recv():
      print(repr(event))

InputDeviceDispatcher(dev)
loop()
