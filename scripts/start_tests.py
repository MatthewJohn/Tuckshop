#!/usr/bin/python

import unittest
import os
import sys
sys.path.append('./')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuckshop.settings_unittest")

import django
django.setup()

from tuckshop.page.tests.credit_tests import CreditTests

if __name__ == '__main__':
    # Set tuckshop devel variable, to ensure that
    # local redis cache is used
    os.environ['TUCKSHOP_DEVEL'] = '1'

    runner = unittest.TextTestRunner(verbosity=4)
    credit_page_tests = CreditTests.suite()
    all_tests = unittest.TestSuite([credit_page_tests])
    sys.exit(not runner.run(all_tests).wasSuccessful())
