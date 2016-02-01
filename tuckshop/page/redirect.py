from tuckshop.page.page_base import PageBase

class Redirect(PageBase):
    """Page for handling redirections"""
    NAME = None
    REQUIRES_AUTHENTICATION = False
    PERMISSION = None

    def __init__(self, request_handler, redirect_url=''):
        super(Redirect, self).__init__(request_handler)
        self.redirect_url = redirect_url
        self.response_code = 302
        self.headers['Location'] = self.redirect_url

    def processTemplate(self):
        pass

    def processPage(self):
        pass

    def processPost(self):
        pass