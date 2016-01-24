import unittest
import os

from tuckshop.page.tests.common import (getPageObject, TestBase, createTestSession,
                                        createTestItem)
from tuckshop.app.models import Inventory, InventoryTransaction, User
from tuckshop.core.config import Config


class CreditTests(TestBase):
    """Performs unit tests on the crdit page"""

    @staticmethod
    def suite():
        suite = unittest.TestSuite()
        suite.addTest(CreditTests('test_list_items'))
        suite.addTest(CreditTests('test_enable_custom'))
        suite.addTest(CreditTests('test_disable_custom'))
        return suite

    def create_test_items(self, user_object):
        """Creates several test inventory items"""
        # Create test items
        test_items = []

        # Create item with no inventory transactions, which should display the amount 'N/A'
        test_items.append(createTestItem('Test Item 1'))

        # Create item, which should be displayed as 1 being available
        test_items.append(createTestItem('Test Item 2',
                                         [[user_object, 123, 124, 2, '']],
                                         [user_object]))
        test_items[1].image_url = 'http://example.com/test_image.png'
        test_items[1].save()

        # Create archived test item, which should not be displayed on page.
        test_items.append(createTestItem('Test Item 3', [[user_object, 254, 255, 2, '']]))
        test_items[2].image_url = 'http://doesnotexist.onpage/image.png'
        test_items[2].archive = True
        test_items[2].save()

        return test_items

    def test_list_items(self):
        """Tests the credit page, ensuring that the
           correct items are displayed on the page"""
        from tuckshop.page.credit import Credit

        # Create session and get user object
        session, cookie = createTestSession(username='test', password='password')
        user_object = User.objects.get(uid='test')

        # Create test items
        test_items = self.create_test_items(user_object)

        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the correct user object has been passed to the template
        self.assertEqual(credit_page.return_vars['user'], user_object)

        # Ensure that the enable custom option matches to the configuration
        self.assertEqual(credit_page.return_vars['enable_custom'], Config.ENABLE_CUSTOM_PAYMENT())

        # Ensure that the current user credit is 0 and the string shown to the user is correct
        self.assertEqual(user_object.getCurrentCredit(), -124)
        self.assertEqual(user_object.getCreditString(), '<font style="color: red">-&pound;1.24</font>')

        # Assert that this has been passed to the template
        self.assertTrue(user_object.getCreditString() in credit_page.request_handler.output)

        # Ensure that the available items are displayed on the page

    def test_item_purchase(self):
        # Create test items
        test_items = self.create_test_items()

        # Attempt to purchase an item

        # Ensure that the item is no longer available
        pass

    def test_non_existent_item_purchase(self):
        # Create test items
        test_items = self.create_test_items()
        pass

    def test_purchase_archived_item(self):
        # Create test items
        test_items = self.create_test_items()
        pass

    def test_enable_custom(self):
        """Ensures that the custom payment is present on the page when the
           configuration is enabled. And ensure functionality works
           as expected"""
        from tuckshop.page.credit import Credit

        os.environ['ENABLE_CUSTOM_PAYMENT'] = "1"

        # Create session and get user object
        session, cookie = createTestSession(username='test', password='password')
        user_object = User.objects.get(uid='test')

        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the enable custom option is set to disabled
        self.assertEqual(credit_page.return_vars['enable_custom'], True)

        # Ensure that the custom box is present on the page
        self.assertTrue("<h3 class='custom-amount'>Custom Amount</h3>" in credit_page.request_handler.output)

        # Attempt to make a custom payment using the credit page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'amount': '120',
                                        'description': ''
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that the request returned an error and no money was removed from the user
        self.assertEqual(credit_page.return_vars['error'], None)
        self.assertTrue('Custom payment is disabled' not in credit_page.request_handler.output)
        self.assertEqual(user_object.getCurrentCredit(), -120)

    def test_disable_custom(self):
        """Ensures that the custom payment is removed from
           the page when the configuration has disabled"""
        from tuckshop.page.credit import Credit

        os.environ['ENABLE_CUSTOM_PAYMENT'] = '0'

        # Create session and get user object
        session, cookie = createTestSession(username='test', password='password')
        user_object = User.objects.get(uid='test')

        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the enable custom option is set to disabled
        self.assertEqual(credit_page.return_vars['enable_custom'], False)

        # Ensure that the custom box is not present on the page
        self.assertFalse("<h3 class='custom-amount'>Custom Amount</h3>" in credit_page.request_handler.output)

        # Attempt to make a custom payment using the credit page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'amount': '120',
                                        'description': ''
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that the request returned an error and no money was removed from the user
        self.assertEqual(credit_page.return_vars['error'], 'Custom payment is disabled')
        self.assertTrue('Custom payment is disabled' in credit_page.request_handler.output)
        self.assertEqual(user_object.getCurrentCredit(), 0)
