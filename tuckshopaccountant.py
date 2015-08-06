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