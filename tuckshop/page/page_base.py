import cgi
import Cookie
import jinja2
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
import sha
import math
from mimetypes import read_mime_types
import time
import os
import re
import traceback

from tuckshop.core.config import TOTAL_PAGE_DISPLAY, APP_NAME
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.redis_connection import RedisConnection
from tuckshop.app.models import User

class PageDoesNotExist(TuckshopException):
    pass


class AuthenticationRequired(TuckshopException):
    pass


class AdminPermissionRequired(TuckshopException):
    pass


class PageBase(object):

    CONTENT_TYPE = 'text/html'
    REQUIRES_AUTHENTICATION = True
    ADMIN_PAGE = True

    @staticmethod
    def getUrlBase(request_handler):
        url_parts = PageBase.getUrlParts(request_handler)
        return url_parts[1] if len(url_parts) else ''

    @staticmethod
    def getUrlParts(request_handler):
        return request_handler.path.split('/')

    def __init__(self, request_handler):
        self.request_handler = request_handler
        self.post_vars = {}
        self.return_vars = {
            'error': None,
            'warning': None,
            'info': None,
            'app_name': APP_NAME,
            'page_name': self.name,
            'page_object': self
        }
        self.headers = {}
        self.response_code = 200
        self.session_id = None
        self.session_id = self.getSessionId()

    @property
    def name(self):
        return self.NAME

    @property
    def template(self):
        return self.TEMPLATE

    @property
    def isAdminPage(self):
        return self.ADMIN_PAGE

    @property
    def requiresAuthentication(self):
        return self.REQUIRES_AUTHENTICATION

    @property
    def contentType(self):
        return self.CONTENT_TYPE

    def getPostVariable(self, name, var_type=None, regex=None, default=None,
                        custom_method=None, possible_values=None, message=None):
        """Performs various checks of post vars and returns the value if checks pass"""
        message = message if message else "%s does not conform" % name
        message = "Error (%%s): %s" % message

        # Check if variable is in post data
        if name not in self.post_vars:
            raise TuckshopException(message % 'PD0101')

        value = self.post_vars[name]

        # If var_type has been passed, attempt to perform it on the variable
        if var_type:
            try:
                var_type(value)
            except ValueError:
                raise TuckshopException(message % 'PD0102')

        # Perform regex on the variable, if it exists
        if regex:
            regex = r'^%s$' % regex
            if not re.match(regex, value):
                raise TuckshopException(message % 'PD0103')

        if possible_values:
            if value not in possible_values:
                raise TuckshopException(message % 'PD0104')

        if custom_method:
            if not custom_method(value):
                raise TuckshopException(message % 'PD0105')

        if var_type:
            return var_type(value)
        else:
            return value

    def isLoggedIn(self):
        if (self.getSessionVar('username')):
            return True
        else:
            return False

    def getCurrentUsername(self):
        if (self.isLoggedIn()):
            return self.getSessionVar('username')
        else:
            return None

    def getCurrentUserObject(self):
        if (self.isLoggedIn()):
            return User.objects.get(uid=self.getCurrentUsername())
        else:
            return None

    def requiresLogin(self):
        """Determines if the page requires authentication
           and whether the user is logged in"""
        if self.requiresAuthentication and not self.isLoggedIn():
            return True
        else:
            return False
    
    def requiresAdminAccess(self):
        """Determines if the page requies admin permissions and
           whether the user has admin permissions"""
        if self.isAdminPage and not self.getCurrentUserObject().admin:
            return True
        else:
            return False

    def checkAuthentication(self):
        if self.requiresLogin() or self.requiresAdminAccess():
            raise Exception('Attempting to process page without required permissions')

    def processHeaders(self):
        # Send response code
        self.request_handler.send_response(self.response_code)

        # Send Content-type header
        self.request_handler.send_header('Content-type', self.contentType)

        # Send headers defined by page
        for key in self.headers:
            self.request_handler.send_header(key, self.headers[key])

        self.request_handler.end_headers()

    def processTemplate(self):
        # Obtain template object
        env = Environment()
        env.loader = FileSystemLoader('./templates/')
        template = env.get_template('%s.html' % self.template)
        self.request_handler.wfile.write(template.render(**self.return_vars))

    def attemptFunction(self, fun):
        try:
            fun()
        except TuckshopException, e:
            self.return_vars['error'] = str(e)
            print 'Handled Error: %s' % str(e)
        except Exception, e:
            self.return_vars['error'] = ('An internal server error occurred. '
                                         'Please contact a member of the TuckShop team immediately.')
            print 'Unhandled error: %s' % str(e)
            print traceback.print_exc()
            self.response_code = 500


    def processRequest(self, post_request):
        """Handles requests by the web server"""
        # Ensure that authentication has been checked before
        # performing any further checks
        self.checkAuthentication()

        # If it was post request, process the POST variables and
        # process POST request
        if post_request:
            self.attemptFunction(self.getPostVariables)
            self.attemptFunction(self.processPost)

        # Process page to determine page content
        self.attemptFunction(self.processPage)

        # Process template
        self.processHeaders()
        self.processTemplate()

    def processPage(self):
        raise NotImplementedError

    def processPost(self):
        raise NotImplementedError

    def getPaginationData(self, current_page, total_pages, url_template):
        if (total_pages <= TOTAL_PAGE_DISPLAY):
            page_range = range(1, total_pages + 1)
        else:
            pages_up_down = int(math.ceil((TOTAL_PAGE_DISPLAY - 1) / 2))
            page_range = range(current_page - pages_up_down, current_page + pages_up_downs + 1)

        page_data = []
        for page_numer in page_range:
            page_data.append(['active' if (page_numer == current_page) else '', url_template % page_numer, page_numer])

        return page_data

    def getPostVariables(self):
        form = cgi.FieldStorage(fp=self.request_handler.rfile,
                                headers=self.request_handler.headers,
                                environ={'REQUEST_METHOD':'POST',
                                         'CONTENT_TYPE':self.request_handler.headers['Content-Type']})

        for field in form.keys():
            self.post_vars[field] = form[field].value

    def getSessionId(self):
        if not self.session_id:
            self.session_id = self.getSession()

        return self.session_id

    def getSession(self, clear_cookie=False):
        cookie = Cookie.SimpleCookie()
        sid = None
        if ('Cookie' in self.request_handler.headers):
            cookie.load(self.request_handler.headers.getheader('Cookie'))
            if ('sid' in cookie and cookie['sid']):
                sid = cookie['sid'].value

        if not sid or clear_cookie:
            sid = sha.new(repr(time.time())).hexdigest()
            cookie['sid'] = sid
            cookie['sid']['expires'] = 24 * 60 * 60
            self.headers['Set-Cookie'] = cookie.output()
            RedisConnection.hset('session_' + sid, 'session_id', sid)

        return sid

    def getSessionVar(self, var):
        return RedisConnection.hget('session_' + self.getSession(), var) or None

    def setSessionVar(self, var, value):
        RedisConnection.hset('session_' + self.getSession(), var, value)

    def getFile(self, content_type, base_dir, file_name):
        file_name = '%s/%s' % (base_dir, file_name)

        if (file_name and os.path.isfile(file_name)):
            content_type = read_mime_types(file_name)
            with open(file_name) as fh:
                return content_type, fh.read()
        else:
            return None, None
