from tuckshop.page.page_base import PageBase
from tuckshop.core.utils import login


class Login(PageBase):
    NAME = 'Login'
    TEMPLATE = 'login'
    REQUIRES_AUTHENTICATION = False
    ADMIN_PAGE = False

    def processPage(self):
        pass

    def processPost(self):
        if ('action' in self.post_vars and self.post_vars['action'] == 'login'):
            self.return_vars['auth_error'] = '<div class="alert alert-danger" role="alert">Incorrect Username and/or Password</div>'
            if 'password' in self.post_vars and 'username' in self.post_vars:
                username = self.post_vars['username']
                password = self.post_vars['password']
                if login(username, password):
                    self.setSessionVar('username', username)
                    self.setSessionVar('password', password)
                    self.return_vars['auth_error'] = None


