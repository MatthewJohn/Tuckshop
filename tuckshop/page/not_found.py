from tuckshop.page.page_base import PageBase

class NotFound(PageBase):
    NAME = '404'
    TEMPLATE = '404'
    REQUIRES_AUTHENTICATION = False
    ADMIN_PAGE = False


    def __init__(self, *args, **kwargs):
        super(NotFound, self).__init__(*args, **kwargs)
        self.response_code = 404

    def processPage(self):
        pass

    def processPost(self):
        pass
