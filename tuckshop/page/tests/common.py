import Cookie
import unittest
from django.core.management import call_command
import os

from tuckshop.settings_unittest import DATABASES
from tuckshop.app.models import (Inventory, InventoryTransaction,
                                 Transaction)
from tuckshop.core.redis_connection import RedisConnection

class FakeFileHandler(object):
    """Provides a fake file handler interface
       for use with the fake request handler"""
    def __init__(self, parent):
        """Sets up object variables for storing test data"""
        self.output = ''
        self.parent = parent

    def wfile(self, value):
        """Performs a fake write and stores the output"""
        # Ensure that headers have been finished
        self.parent.unittest.assertTrue(self.parent.headers_finished)
        self.output += value

class FakeHeaders(dict):
    """Fake headers handler"""
    def getheader(self, key):
        """Method to return item from dict"""
        return self[key]

class FakeHandler(object):
    """Provides a fake request handler for performing
       unit tests and checking the set values"""

    def __init__(self, unittest, path):
        """Stores the necessary object variables"""
        self.wfile = FakeFileHandler(self)
        self.unittest = unittest
        self.path = path
        self.output = ''
        self.headers = FakeHeaders()
        self.headers_finished = False

    def send_header(self, key, value):
        """Fakes the send_header function.
           Ensures that the header has not already been
           set and appends the value to the headers dict"""
        self.unittest.assertFalse(key in self.headers)
        self.headers[key] = value

    def end_headers(self):
        """Fakes the end_headers function.
           Ensures that the function has not been run before and
           sets the end_headers to true"""
        self.unittest.assertFalse(self.end_headers)
        self.end_headers = True

def getPageObject(page_class, path, unittest, headers, post_variables={}):
    """Obtains a page object, passing a fake handler and
       overriding the getPostVariables method"""

    def getPostVariables(self):
        """Set the post variables to the variables
           passed to the getPageObject method"""
        self.post_variables = post_variables

    # Create fake handler for page request
    fake_handler = FakeHandler(unittest, path)

    # Add test headers to headers object
    for header_key in headers:
        fake_handler.headers[header_key] = headers[header_key]

    # Obtain the page object
    page_object = page_class(fake_handler)

    # Override the getPostVariables method
    page_object.getPostVariables = getPostVariables

    # Return page object
    return page_object

def createTestItem(item_name, inventory_transactions=[],
                   transactions=[]):
    """Create test items in the database.
       inventory_transactions =
       [[
            user, cost, sale_price, quantity, description
        ], ...]
       transactions = [user, user, ...]"""
    # Create inventory object
    inventory_object = Inventory(name=item_name)
    inventory_object.save()

    # Create inventory transactions to add stock to item
    for inventory_transaction in inventory_transactions:
        user = inventory_transaction[0]
        cost = inventory_transaction[1]
        sale_price = inventory_transaction[2]
        quantity = inventory_transaction[3]
        description = inventory_transaction[4]
        InventoryTransaction(inventory=inventory_object, user=user,
                             quantity=quantity, cost=cost, sale_price=sale_price,
                             description=description).save()

    # Add transaction objects to add sales
    for transaction in transactions:
        user.removeCredit(inventory=inventory_object)

    return inventory_object

def createTestSession(username=None, password=None):
    """Creates a test session and, if provided, sets up authentication"""
    # Create session sid
    sid = 'test_session'
    cookie = Cookie.SimpleCookie()
    cookie['sid'] = sid
    cookie['sid']['expires'] = 24 * 60 * 60
    RedisConnection.hset('session_' + sid, 'username', username)
    RedisConnection.hset('session_' + sid, 'password', password)
    return sid, cookie.output()

def TearDown():
    """Tear down database, removing all test data"""
    pass

class TestBase(unittest.TestCase):
    def setUp(self):
        """Perform required tasks for each test"""
        # Create test database
        #  - Run django syncdb, to setup unittest DB
        call_command('syncdb', interactive=False)

    def tearDown(self):
        """Perform common teardown tasks"""
        # Delete test database
        os.remove(DATABASES['default']['NAME'])
