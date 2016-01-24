import unittest

from tuckshop.page.tests.common import getPageObject, TestBase, createTestSession
from tuckshop.app.models import Inventory, InventoryTransaction
from tuckshop.page.credit import Credit


class CreditTests(TestBase):
    """Performs unit tests on the crdit page"""

    @staticmethod
    def suite():
        suite = unittest.TestSuite()
        suite.addTest(CreditTests('test_list_items'))
        return suite

    def test_list_items(self):
        """Tests the credit page, ensuring that the
           correct items are displayed on the page"""
        # Add 3 items to the database
        session, cookie = createTestSession(username='test', password='password')
        test_items = []
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie})
        credit_page.processRequest(post_request=False)
        print credit_page.request_handler.output