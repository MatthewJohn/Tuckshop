from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound
from tuckshop.page.login import Login
from tuckshop.page.credit import Credit
from tuckshop.page.redirect import Redirect
from tuckshop.page.static_file import JS, CSS, Font

class Factory(object):

    @staticmethod
    def getPageObject(request_handler):
        name = PageBase.getUrlBase(request_handler)
        page_object = None
        if name == 'credit' or name == '':
            page_object = Credit(request_handler)
        elif name == 'login':
            page_object = Login(request_handler)
        elif name == 'js':
            page_object = JS(request_handler)
        elif name == 'css':
            page_object = CSS(request_handler)
        elif name == 'font':
            page_object = Font(request_handler)
        else:
            page_object = NotFound(request_handler)

        if page_object.requiresLogin():
            # If page requires login, redirect to login page
            current_url = PageBase.getUrlParts(request_handler)
            current_url = current_url[1:]
            redirect_url = '/login/%s' % '/'.join(current_url)
            page_object = Redirect(request_handler, redirect_url)
        elif page_object.requiresAdminAccess():
            page_object = NotFound(request_handler)

        return page_object
