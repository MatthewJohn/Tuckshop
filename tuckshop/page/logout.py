from tuckshop.page.redirect import Redirect

class Logout(Redirect):
    """Logs the user out, clearing the session and redirect to the root URL"""

    NAME = 'Logout'
    MENU_ORDER = 6
    URL = '/logout'

    def __init__(self, *args, **kwargs):
        super(Logout, self).__init__(redirect_url='/', *args, **kwargs)

    def processPage(self):
        self.setSessionVar('username', None)
        self.setSessionVar('password', None)
        self.session_id = self.getSession(clear_cookie=True)
