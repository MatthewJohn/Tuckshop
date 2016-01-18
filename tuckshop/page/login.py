from tuckshop.page.page_base import PageBase
from tuckshop.page.redirect import Redirect
from tuckshop.core.utils import login


class Login(PageBase):
    NAME = 'Login'
    TEMPLATE = 'login'
    REQUIRES_AUTHENTICATION = False
    ADMIN_PAGE = False

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.redirect = None

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
                    redirect_url = '/%s' % '/'.join(Login.getUrlParts(self.request_handler)[2:])
                    self.redirect = Redirect(self.request_handler, redirect_url)

    def processPage(self):
        if self.redirect:
            self.redirect.processPage()

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
