from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound
from tuckshop.page.login import Login
from tuckshop.page.credit import Credit

class Factory(object):

    @staticmethod
    def getPageObject(request_handler):
        name = PageBase.getUrlBase(request_handler)
        page_object = None
        if name == 'credit' or name == '':
            page_object = Credit(request_handler)
        else:
            page_object = NotFound(request_handler)

        if page_object.requiresLogin():
            page_object = Login(request_handler)
        elif page_object.requiresAdminAccess():
            page_object = NotFound(request_handler)

        return page_object
