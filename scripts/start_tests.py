#!/usr/bin/python

import unittest
import os
import sys
sys.path.append('./')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuckshop.settings")

import django
django.setup()

from tuckshop.core.tests.utils_tests import UtilsTests

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=4)
    utils_test_suite = UtilsTests.suite()
    all_tests = unittest.TestSuite([utils_test_suite])
    sys.exit(not runner.run(all_tests).wasSuccessful())
