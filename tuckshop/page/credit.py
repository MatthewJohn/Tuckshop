from tuckshop.page.page_base import PageBase

class Credit(PageBase):

    NAME = 'Credit'
    TEMPLATE = 'credit'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = False

    def processPage(self):
        pass

    def processPost(self):
        pass
