from tuckshop.page.page_base import PageBase

class NotFound(PageBase):
    NAME = '404'
    TEMPLATE = '404'
    REQUIRES_AUTHENTICATION = False
    PERMISSION = None


    def __init__(self, *args, **kwargs):
        super(NotFound, self).__init__(*args, **kwargs)
        self.response_code = 404
        self.return_vars['path'] = self.request_handler.path

    def processPage(self):
        pass

    def processPost(self):
        pass
