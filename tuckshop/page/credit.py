from tuckshop.page.page_base import PageBase

class Credit(PageBase):

    NAME = 'Credit'
    TEMPLATE = 'credit'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        self.return_vars['user'] = self.getCurrentUserObject()

    def processPost(self):
        pass
