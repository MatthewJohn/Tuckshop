
import mock
import unittest

class UtilsTests(unittest.TestCase):
    """Performs unit tests on the utils class"""

    @staticmethod
    def suite():
        suite = unittest.TestSuite()
        suite.addTest(UtilsTests('test_login'))
        return suite

    @mock.patch('tuckshop.core.config')
    @mock.patch('tuckshop.app.models.User', spec=True)
    def test_login(self, mock_config, mock_user_class):
        with mock.patch.dict('os.environ', values={'TUCKSHOP_DEVEL': 'True'}):
            from tuckshop.core.utils import login

            # Test failure cases
            failure_cases = [['', ''], ['mc', ''], ['', 'asd'], ['test', 'nonpassword']]
            for failure_case in failure_cases:
                self.assertFalse(login(failure_case[0], failure_case[1]))

            login_return = login(username='mc', password='password')
            print mock_user_class.call_count

        mock_config.LDAP_SERVER = 'test_ldap_server'