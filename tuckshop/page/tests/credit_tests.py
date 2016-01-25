import unittest
import os

from tuckshop.page.tests.common import (getPageObject, TestBase,
                                        createTestItem)
from tuckshop.app.models import Transaction
from tuckshop.core.config import Config
from tuckshop.page.credit import Credit


class CreditTests(TestBase):
    """Performs unit tests on the crdit page"""

    @staticmethod
    def suite():
        """Returns test suite for credit page"""
        suite = unittest.TestSuite()
        suite.addTest(CreditTests('test_list_items'))
        suite.addTest(CreditTests('test_item_purchase'))
        suite.addTest(CreditTests('test_non_existent_item_purchase'))
        suite.addTest(CreditTests('test_purchase_archived_item'))
        suite.addTest(CreditTests('test_enable_custom'))
        suite.addTest(CreditTests('test_disable_custom'))
        return suite

    def test_list_items(self):
        """Tests the credit page, ensuring that the
           correct items are displayed on the page"""
        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': self.cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the correct user object has been passed to the template
        self.assertEqual(credit_page.return_vars['user'], self.user_object)

        # Ensure that the enable custom option matches to the configuration
        self.assertEqual(credit_page.return_vars['enable_custom'], Config.ENABLE_CUSTOM_PAYMENT())

        # Ensure that the current user credit is 0 and the string shown to the user is correct
        self.assertEqual(self.user_object.getCurrentCredit(), -124)
        self.assertEqual(self.user_object.getCreditString(),
                         '<font style="color: red">-&pound;1.24</font>')

        # Assert that this has been passed to the template
        self.assertTrue(self.user_object.getCreditString() in credit_page.request_handler.output)

        # Ensure that the items are passed to the return vars
        self.assertTrue(self.test_items[0] in credit_page.return_vars['inventory'])
        self.assertTrue(self.test_items[1] in credit_page.return_vars['inventory'])

        # Ensure that the archived item is not present
        self.assertTrue(self.test_items[2] not in credit_page.return_vars['inventory'])

        # Ensure that the available items are displayed on the page
        self.assertTrue(self.test_items[0].name in credit_page.request_handler.output)
        self.assertTrue(self.test_items[0].getSalePriceString() in
                        credit_page.request_handler.output)
        self.assertTrue(self.test_items[1].name in
                        credit_page.request_handler.output)
        self.assertTrue(self.test_items[1].getSalePriceString() in
                        credit_page.request_handler.output)
        self.assertTrue(self.test_items[2].name not in
                        credit_page.request_handler.output)
        self.assertTrue(self.test_items[2].getSalePriceString() not in
                        credit_page.request_handler.output)

    def test_item_purchase(self):
        """Test purchasing items"""
        # Purchase an item
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'item_id': self.test_items[1].pk
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that the user has been debitted
        self.user_object.refresh_from_db()
        self.assertEqual(self.user_object.getCurrentCredit(), -248)

        # Ensure that the amount of the item has now risen to the price of the
        # second inventory transaction
        self.assertTrue('&pound;2.00' in credit_page.request_handler.output)

        # Purchase the same item and ensure that the new price has been used
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'item_id': self.test_items[1].pk
                                    })
        credit_page.processRequest(post_request=True)

        self.user_object.refresh_from_db()
        self.assertEqual(self.user_object.getCurrentCredit(), -448)

        # Ensure that the price is now disabled
        self.assertEqual(self.test_items[1].getQuantityRemaining(), 0)
        self.assertTrue(('<input type="submit" class="btn btn-primary" value="&pound;2.00"'
                         ' role="button" disabled/>') in credit_page.request_handler.output)

        # Attempt to purchase another item and ensure an error is displayed
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'item_id': self.test_items[1].pk
                                    })
        credit_page.processRequest(post_request=True)

        # Assert that an error was displayed to the user and credit has not changed
        self.assertEqual(credit_page.return_vars['error'], 'There are no items in stock')
        self.user_object.refresh_from_db()
        self.assertEqual(self.user_object.getCurrentCredit(), -448)

    def test_non_existent_item_purchase(self):
        """Test the purchase of non-existent items"""
        # Purchase an item
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'item_id': 5
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that user's account has not been debitted.
        self.assertEqual(self.user_object.getCurrentCredit(), -124)

    def test_purchase_archived_item(self):
        """Tests attempts to purchasing archived items"""
        original_quantity = self.test_items[2].getQuantityRemaining()

        # Purchase an item
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'item_id': self.test_items[2].pk
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that user's account has not been debitted.
        self.assertEqual(self.user_object.getCurrentCredit(), -124)

        # Ensure error is displayed to user 
        self.assertEqual(credit_page.return_vars['error'], 'Item is archived')

        # Ensure item quantity has not changed
        self.test_items[2].refresh_from_db()
        self.assertEqual(self.test_items[2].getQuantityRemaining(), original_quantity)

        # Ensure that there are no new transactions
        self.assertEqual(
            len(Transaction.objects.filter(
                inventory_transaction=self.test_items[2].getCurrentInventoryTransaction()
            )),
            0
        )

    def test_enable_custom(self):
        """Ensures that the custom payment is present on the page when the
           configuration is enabled. And ensure functionality works
           as expected"""
        # Enable custom payments in environmental settings
        os.environ['ENABLE_CUSTOM_PAYMENT'] = '1'

        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': self.cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the enable custom option is set to disabled
        self.assertEqual(credit_page.return_vars['enable_custom'], True)

        # Ensure that the custom box is present on the page
        self.assertTrue('<h3 class=\'custom-amount\'>Custom Amount</h3>' in
                        credit_page.request_handler.output)

        # Attempt to make a custom payment using the credit page
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'amount': '120',
                                        'description': ''
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that the request returned an error and no money was removed from the user
        self.assertEqual(credit_page.return_vars['error'], None)
        self.assertTrue('Custom payment is disabled' not in credit_page.request_handler.output)
        self.assertEqual(self.user_object.getCurrentCredit(), -244)

    def test_disable_custom(self):
        """Ensures that the custom payment is removed from
           the page when the configuration has disabled"""
        os.environ['ENABLE_CUSTOM_PAYMENT'] = '0'

        # Perform request to page
        credit_page = getPageObject(Credit, path='', unittest=self, headers={'Cookie': self.cookie})
        credit_page.processRequest(post_request=False)

        # Ensure that the enable custom option is set to disabled
        self.assertEqual(credit_page.return_vars['enable_custom'], False)

        # Ensure that the custom box is not present on the page
        self.assertFalse('<h3 class=\'custom-amount\'>Custom Amount</h3>' in
                         credit_page.request_handler.output)

        # Attempt to make a custom payment using the credit page
        credit_page = getPageObject(Credit, path='', unittest=self,
                                    headers={'Cookie': self.cookie},
                                    post_variables={
                                        'action': 'pay',
                                        'amount': '120',
                                        'description': ''
                                    })
        credit_page.processRequest(post_request=True)

        # Ensure that the request returned an error and no money was removed from the user
        self.assertEqual(credit_page.return_vars['error'], 'Custom payment is disabled')
        self.assertTrue('Custom payment is disabled' in credit_page.request_handler.output)
        self.assertEqual(self.user_object.getCurrentCredit(), -124)
