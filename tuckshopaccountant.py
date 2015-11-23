#!/usr/bin/python

import sqlite3
import os

from decimal import Decimal, getcontext
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
import math
import time
from mimetypes import read_mime_types

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuckshop.settings")

import django
django.setup()

from tuckshop.app.models import *
from tuckshop.app.functions import *
from tuckshop.app.config import *

TRANSACTION_PAGE_SIZE = 10
TOTAL_PAGE_DISPLAY = 7
LDAP_SERVER = 'localhost'
APP_NAME = 'ITDev Tuck Shop'

print os.environ
# Setup listener for RFID to obtain login details
# from asyncore import file_dispatcher, loop
# from evdev import InputDevice, categorize, ecodes
# dev = InputDevice('/dev/input/event8')

# class InputDeviceDispatcher(file_dispatcher):
#     def __init__(self, device):
#         self.device = device
#         file_dispatcher.__init__(self, device)

#     def recv(self, ign=None):
#         return self.device.read()

#     def handle_read(self):
#         for event in self.recv():
#             print(repr(event))

#InputDeviceDispatcher(dev)
#loop()

env = Environment()
env.loader = FileSystemLoader('./templates/')

sessions = {}

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
            if content_type is None:
                content_type = read_mime_types(file_name)
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
        self.wfile.write(template.render(app_name=APP_NAME, page_name='Login', warning=error, url=self.path))

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

    def getCurrentUserObject(self):
        if (self.isLoggedIn()):
            user_object = self.getSessionVar('user_object')
            if (not user_object):
                user_object = User.objects.get(uid=self.getCurrentUsername())
                self.setSessionVar('user_object', user_object)
            else:
                user_object.refresh_from_db()
            return user_object
        else:
            return None

    def do_GET(self, post_vars={}):
        # Get file
        if 'error' not in post_vars:
            post_vars['error'] = None
        self.post_vars = post_vars
        split_path = self.path.split('/')
        base_dir = split_path[1] if (len(split_path) > 1) else ''
        file_name = split_path[2] if len(split_path) == 3 else ''

        valid_urls = ['', 'credit', 'logout', 'history', 'stock']
        if self.isLoggedIn() and self.getCurrentUserObject().admin:
            valid_urls.append('admin')

        if (base_dir == 'css'):
            self.getFile('text/css', 'css', file_name)

        elif (base_dir == 'js'):
            self.getFile('text/javascript', 'js', file_name)

        elif base_dir == 'fonts':
            self.getFile(None, 'fonts', file_name)

        elif (base_dir == 'logout'):
            self.send_response(200)
            self.getSession(clear_cookie=True)
            self.end_headers()
            self.sendLogin()

        elif (base_dir in valid_urls):
            self.getSession()

            if ('set_response' not in post_vars):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

            if (not self.isLoggedIn()):
                self.sendLogin()
            else:
                user_object = self.getCurrentUserObject()

                if (base_dir == '' or base_dir == 'credit'):
                    template = env.get_template('credit.html')
                    inventory_items = Inventory.getAvailableItems()
                    self.wfile.write(template.render(app_name=APP_NAME, inventory=inventory_items,
                                                     page_name='Credit', user=self.getCurrentUserObject(),
                                                     error=post_vars['error']))

                elif (base_dir == 'history'):
                    template = env.get_template('history.html')
                    transaction_history = self.getCurrentUserObject().getTransactionHistory(include_inventory_history=True)

                    if (len(transaction_history) > TRANSACTION_PAGE_SIZE):
                        page_number = int(split_path[2]) if len(split_path) == 3 else 1
                        total_pages = int(math.ceil((len(transaction_history) - 1) / TRANSACTION_PAGE_SIZE)) + 1
                        page_data = self.getPageData(page_number, total_pages, '/history/%s')
                        array_start = (page_number - 1) * TRANSACTION_PAGE_SIZE
                        array_end = page_number * TRANSACTION_PAGE_SIZE
                        transaction_history = transaction_history[array_start:array_end]

                    else:
                        page_data = []

                    self.wfile.write(template.render(app_name=APP_NAME, page_name='History',
                                                     transaction_history=transaction_history,
                                                     page_data=page_data, error=post_vars['error']))

                elif (base_dir == 'stock'):
                    template = env.get_template('stock.html')
                    inventory_items = Inventory.objects.all().order_by('archive', 'name', '-quantity')
                    active_items = Inventory.objects.filter(archive=False)
                    self.wfile.write(template.render(app_name=APP_NAME, page_name='Stock',
                                                     inventory_items=inventory_items,
                                                     active_items=active_items, error=post_vars['error']))

                elif base_dir == 'admin' and user_object.admin:
                    template = env.get_template('admin.html')
                    users = User.objects.all()
                    unapproved_transactions = InventoryTransaction.objects.filter(approved=False).order_by('-timestamp')
                    self.wfile.write(template.render(app_name=APP_NAME, page_name='Admin',
                                                     users=users, error=post_vars['error'],
                                                     unapproved_transactions=unapproved_transactions))

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            template = env.get_template('404.html')
            self.wfile.write(template.render(app_name=APP_NAME, page_name='History',
                                             path=self.path, error=post_vars['error']))

        return

    def getPageData(self, current_page, total_pages, url_template):
        if (total_pages <= TOTAL_PAGE_DISPLAY):
            page_range = range(1, total_pages + 1)
        else:
            pages_up_down = int(math.ceil((TOTAL_PAGE_DISPLAY - 1) / 2))
            page_range = range(current_page - pages_up_down, current_page + pages_up_downs + 1)

        page_data = []
        for page_numer in page_range:
            page_data.append(['active' if (page_numer == current_page) else '', url_template % page_numer, page_numer])

        return page_data

    def getPostVariables(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type']})

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
                if ('password' in variables and 'username' in variables and
                        self.login(variables['username'], variables['password'])):
                    post_vars['auth_failure'] = False
            elif self.isLoggedIn():
                if base_dir == 'credit':
                    post_vars = self.processCreditPostRequest(variables, post_vars)
                elif base_dir == 'stock':
                    post_vars = self.processStockPostRequest(variables, post_vars)

                elif (base_dir == 'admin' and self.getCurrentUserObject().admin):
                    post_vars = self.processAdminPostRequest(variables, post_vars)

        self.do_GET(post_vars=post_vars)
        return

    def login(self, username, password):
        if (login(username, password)):
            self.setSessionVar('username', username)
            self.setSessionVar('password', password)
            return True
        else:
            return False

    def processAdminPostRequest(self, variables, post_vars):

        action = variables['action']
        if action == 'approve':
            inv_trans_object = InventoryTransaction.objects.get(pk=variables['transaction_id'])
            inv_trans_object.approve()
        elif action == 'Add':
            user_object = User.objects.get(uid=variables['uid'])
            user_object.addCredit(int(variables['amount']))
        elif action == 'Remove':
            user_object = User.objects.get(uid=variables['uid'])
            user_object.removeCredit(int(variables['amount']))

        return post_vars


    def processCreditPostRequest(self, variables, post_vars):
        action = variables['action']
        if (action == 'pay' and 'amount' in variables):
            self.getCurrentUserObject().removeCredit(int(variables['amount']))
        elif (action == 'pay' and 'item_id' in variables):
            inventory_object = Inventory.objects.get(pk=variables['item_id'])
            self.getCurrentUserObject().removeCredit(inventory=inventory_object)

        return post_vars

    def processStockPostRequest(self, variables, post_vars):
        action = None if 'action' not in variables else variables['action']
        if (variables['action'] == 'Add Stock'):
            if not int(variables['quantity'] or int(variables['quantity']) < 1):
                print "'I don't care"
                post_vars['error'] = 'Quantity must be a positive integer'
                return post_vars

            quantity = int(variables['quantity'])
            inventory_id = int(variables['inv_id'])
            inventory_object = Inventory.objects.get(pk=inventory_id)

            if (variables['cost_type'] == 'total'):
                cost = int(float(variables['cost_total']) * 100)

            elif (variables['cost_type'] == 'each'):
                cost = (int(float(variables['cost_each']) * 100) * quantity)

            inventory_object.addItems(quantity, self.getCurrentUserObject(), cost)

        elif (action == 'update'):
            if 'item_id' not in variables:
                post_vars['error'] = 'Item ID not available'
                return post_vars
            item = Inventory.objects.get(pk=int(variables['item_id']))
            item.name = variables['item_name']
            getcontext().prec = 2
            item.price = Decimal(variables['item_price'])
            item.url = variables['image_url']
            item.save()

        elif action == 'archive':
            if 'item_id' not in variables:
                post_vars['error'] = 'Item ID not available'
                return post_vars
            item = Inventory.objects.get(pk=int(variables['item_id']))

            item.archive = (not item.archive)
            item.save()

        elif action == 'delete':
            if 'item_id' not in variables:
                post_vars['error'] = 'Item ID not available'
                return post_vars
            item = Inventory.objects.get(pk=int(variables['item_id']))
            if ((InventoryTransaction.objects.filter(inventory=item) or
                 Transaction.objects.filter(inventory=item))):
                post_vars['error'] = 'Cannot delete item that has transactions related to it'
                return post_vars
            item.delete()

        elif action == 'create':
            if 'item_price' in variables:
                price = int(variables['item_price'])
            else:
                price = 0

            if 'item_archive' in variables:
                archive = bool(variables['item_archive'])
            else:
                archive = False

            if 'image_url' in  variables:
                image_url = str(variables['image_url'])
            else:
                image_url = ''

            item = Inventory(name=str(variables['item_name']), price=price,
                             image_url=image_url, archive=archive)

            item.save()

        return post_vars

if (__name__ == '__main__'):

    server_address = ('', 5000)
    httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()
