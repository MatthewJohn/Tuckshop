from os import environ

from tuckshop.page.page_base import PageBase, InvalidPostVariable
from tuckshop.page.redirect import Redirect
from tuckshop.core.utils import login


class Login(PageBase):
    NAME = 'Login'
    TEMPLATE = 'login'
    REQUIRES_AUTHENTICATION = False
    PERMISSION = None

    def __init__(self, *args, **kwargs):
        """Override the base init method to setup
           redirect object"""
        super(Login, self).__init__(*args, **kwargs)
        self.redirect = None

    @staticmethod
    def getLoginUrl(request_handler):
        """Determines the login url, which will redirect
           back to the current page after a successful login"""
        current_url = PageBase.getUrlParts(request_handler)
        current_url = current_url[1:]
        return '/login/%s' % '/'.join(current_url)

    def processPost(self):
        action = self.getPostVariable(name='action', possible_values=['login'])
        if (action == 'login'):
            self.return_vars['auth_error'] = '<div class="alert alert-danger" role="alert">Incorrect Username and/or Password</div>'
            username = None
            password = None
            try:
                username = self.getPostVariable(name='username', var_type=str, regex='[a-zA-Z0-9]+').lower()
                password = self.getPostVariable(name='password', var_type=str)
            except InvalidPostVariable:
                return

            if username and password and login(username, password):
                self.setSessionVar('username', username)
                self.return_vars['auth_error'] = None
                redirect_url = '/%s' % '/'.join(Login.getUrlParts(self.request_handler)[2:])
                self.redirect = Redirect(request_handler=self.request_handler, redirect_url=redirect_url)

    def processPage(self):
        if self.redirect:
            self.redirect.processPage()
        if 'TUCKSHOP_DEVEL' in environ and environ['TUCKSHOP_DEVEL']:
            self.return_vars['info'] = ('Tuckshop is in development mode.<br />'
                                        'Login using any username with password \'password\'.<br />'
                                        'The username for the default admin account is \'aa\'<br />')

    def processHeaders(self):
        if self.redirect:
            self.redirect.processHeaders()
        else:
            super(Login, self).processHeaders()

    def processTemplate(self):
        if self.redirect:
            self.redirect.processTemplate()
        else:
            super(Login, self).processTemplate()
