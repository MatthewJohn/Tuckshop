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
import json
import re
import traceback
from django.db import transaction

from tuckshop.core.config import Config
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.core.redis_connection import RedisConnection
from tuckshop.app.models import User
from tuckshop.core.permission import Permission


class PageDoesNotExist(TuckshopException):
    pass


class AuthenticationRequired(TuckshopException):
    pass


class AdminPermissionRequired(TuckshopException):
    pass


class VariableVerificationTypes(object):
    """Provides methods of passing verification
       types to the getPostVariable method"""
    POSITIVE = 0
    NON_NEGATIVE = 1
    FLOAT_MONEY = 2
    NOT_EMPTY = 3


class InvalidPostVariable(TuckshopException):
    """Post variable does not comform to specified restraints"""
    pass


class PageBase(object):

    CONTENT_TYPE = 'text/html'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.ADMIN
    POST_URL = ''
    SUB_MENU = None
    MENU_ORDER = None
    MENU_NAME = None
    SUB_MENU_ORDER = None

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
        self.headers = {}
        self.response_code = 200
        self.session_id = None
        self.getSessionId()
        self.getReturnVars()
        self.post_redirect_url_custom = None

    def getReturnVars(self):
        return_vars_key = 'return_vars'
        if self.getSessionVar(return_vars_key) and self.getSessionVar(return_vars_key) != 'unset':
            self.return_vars = json.loads(self.getSessionVar(return_vars_key))
            self.setSessionVar(return_vars_key, 'unset')

        else:
            self.return_vars = {
                'error': None,
                'warning': None,
                'info': None,
                'app_name': Config.APP_NAME(),
                'page_name': self.name
            }

    @property
    def name(self):
        return self.NAME

    @property
    def template(self):
        return self.TEMPLATE

    @property
    def permission(self):
        return self.PERMISSION

    @property
    def requiresAuthentication(self):
        return self.REQUIRES_AUTHENTICATION

    @property
    def contentType(self):
        return self.CONTENT_TYPE

    @property
    def menuName(self):
        return self.MENU_NAME if self.MENU_NAME else self.NAME

    @property
    def post_redirect_url(self):
        return self.post_redirect_url_custom or self.POST_URL

    def getPostVariable(self, name, var_type=None, regex=None, default=None,
                        set_default=False, custom_method=None, possible_values=None,
                        special=[], message=None, max_length=None):
        """Performs various checks of post vars and returns the value if checks pass"""
        message = message if message else "%s does not conform" % name
        message = "Error (%%s): %s" % message

        # If max-length has not been specified and the variable is a string,
        # default to limit to 255 characters
        if var_type is str:
            max_length = 255

        # Check if variable is in post data
        if name not in self.post_vars:
            if set_default:
                return default
            else:
                raise InvalidPostVariable(message % 'PD0101')

        # Obtain the value from post data
        value = self.post_vars[name]
        if var_type is str:
            # If the var_type is string, convert unicode characters
            value = str(self.post_vars[name].decode('iso-8859-1').encode('utf8'))
        else:
            value = self.post_vars[name]

        # If a type has not been specified and a 'special' case has been,
        # set the var_type to an appropriate value.
        if not var_type:
            if (VariableVerificationTypes.POSITIVE in special
                    or VariableVerificationTypes.NON_NEGATIVE in special
                    or VariableVerificationTypes.FLOAT_MONEY in special):
                var_type = float

        # If var_type has been passed, attempt to perform it on the variable
        if var_type:
            try:
                value = var_type(value)
            except ValueError:
                raise InvalidPostVariable(message % 'PD0102')

            # Ensure that the valueof the item does not change
            # when the type is applied
            if value != var_type(value):
                raise InvalidPostVariable(message % 'PD103')

        # Perform regex on the variable, if it exists
        if regex:
            regex = r'^%s$' % regex
            if not re.match(regex, value):
                raise InvalidPostVariable(message % 'PD0104')

        # If a list of possible value has been passed, ensure
        # that the value is in the list.
        if possible_values:
            if value not in possible_values:
                raise InvalidPostVariable(message % 'PD0105')

        # If a custom method has been provided, run it
        # and raise an except if it returns False
        if custom_method:
            if not custom_method(value):
                raise InvalidPostVariable(message % 'PD0106')

        # Perform pre-defined checks if a 'special' case has been passed
        # Ensure value is a positive integer
        if VariableVerificationTypes.POSITIVE in special and value <= 0:
            raise InvalidPostVariable(message % 'PD0107')

        # Ensure value is a non-negative integer
        if VariableVerificationTypes.NON_NEGATIVE in special and value < 0:
            raise InvalidPostVariable(message % 'PD0108')

        # Determin if, when rounded to 2dp, whether the value still equals
        # the original value.
        if VariableVerificationTypes.FLOAT_MONEY in special and round(value, 2) != value:
            raise InvalidPostVariable(message % 'PD0109')

        if VariableVerificationTypes.NOT_EMPTY in special and value == '':
            raise InvalidPostVariable(message % 'PD0110')

        if max_length:
            if len(value) > max_length:
                raise TuckshopException(message % 'PDO0111')

        return value

    def getSubMenu(self):
        if self.SUB_MENU:
            rows = []
            template = """<ul class="nav nav-tabs">%s</ul>"""
            row_template = """<li role="presentation"%s><a href="%s">%s</a></li>"""
            for page_class in sorted(self.SUB_MENU.__subclasses__(), key=lambda x: x.SUB_MENU_ORDER):
                page_object = page_class(self.request_handler)
                if not page_object.requiresPermission():
                    is_active = ' class="active"' if (self.__class__.__name__ == page_class.__name__) else ''
                    rows.append(row_template % (is_active, page_object.URL, page_object.NAME))

            return template % ''.join(rows)
        else:
            return ''

    def getMenu(self):
        rows = []
        template = """<ul class="nav nav-pills nav-justified">%s</ul>"""
        row_template = """<li role="presentation"%s><a href="%s">%s</a></li>"""
        if self.isLoggedIn():
            for page_class in sorted(PageBase.all_subclasses(PageBase), key=lambda x: x.MENU_ORDER):
                if page_class.MENU_ORDER:
                    page_object = page_class(self.request_handler)

                    if not page_object.requiresPermission():
                        is_active = ' class="active"' if (self.__class__.__name__ == page_class.__name__) else ''
                        rows.append(row_template % (is_active, page_object.URL, page_object.menuName))
        else:
            rows.append(row_template % ('', '/login', 'Login'))

        return template % ''.join(rows)

    @staticmethod
    def all_subclasses(cls):
        all_subclasses = []

        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(PageBase.all_subclasses(subclass))

        return all_subclasses

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
    
    def requiresPermission(self):
        """Determines if the page requies admin permissions and
           whether the user has admin permissions"""
        if self.permission and not self.getCurrentUserObject().checkPermission(self.permission):
            return True
        else:
            return False

    def checkAuthentication(self):
        if self.requiresLogin() or self.requiresPermission():
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
        self.return_vars['page_object'] = self
        self.request_handler.wfile.write(unicode(template.render(**self.return_vars)).encode('latin1'))

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
            print 'POST: %s' % self.post_vars
            print 'Headers: %s' % self.request_handler.headers
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

            # Perform the post request handling in a database
            # transaction, to ENSURE data entegrity
            with transaction.atomic():
                self.attemptFunction(self.processPost)
                self.postRedirect()

        else:
            # Process page to determine page content
            self.attemptFunction(self.processPage)

        # Process headers
        self.processHeaders()

        if not post_request:
            # Process template
            self.processTemplate()

    def processPage(self):
        raise NotImplementedError

    def processPost(self):
        raise NotImplementedError

    def postRedirect(self):
        """Perform redirect after post request"""
        # Convert return vars to session variables
        self.setSessionVar('return_vars', json.dumps(self.return_vars))
        self.response_code = 302
        self.headers['Location'] = self.post_redirect_url

    def getPaginationData(self, current_page, total_pages, url_template):
        if total_pages <= Config.TOTAL_PAGE_DISPLAY():
            page_range = range(1, total_pages + 1)
        else:
            pages_up_down = int(math.ceil((Config.TOTAL_PAGE_DISPLAY() - 1) / 2))

            # Determine if the lower limit is based on the minimum page (1)
            # or on the current  page - the TOTAL_PAGE_DISPLAY
            if (current_page - pages_up_down) < 1:
                lower_page = 1
            else:
                lower_page = (current_page - pages_up_down)

            # Determine if upper limit is based on the total pages
            # or on the current page + the TOTAL_PAGE_DISPLAY
            if (current_page + pages_up_down) > total_pages:
                upper_page = (total_pages + 1)
            else:
                upper_page = (current_page + pages_up_down + 1)
            page_range = range(lower_page, upper_page)

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
        sid = None
        if ('Cookie' in self.request_handler.headers):
            cookie = Cookie.SimpleCookie()
            cookie.load(self.request_handler.headers.getheader('Cookie'))
            if ('sid' in cookie and cookie['sid']):
                sid = cookie['sid'].value

        if not sid or clear_cookie:
            cookie = Cookie.SimpleCookie()
            sid = str(sha.new(repr(time.time())).hexdigest())
            cookie['sid'] = sid
            cookie['sid']['path'] = '/'
            expires = (time.time() + 14 * 24 * 3600)
            cookie['sid']['expires'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expires))
            cookie_output = cookie.output().split(': ')
            RedisConnection.hset('session_' + str(sid), 'exists', '1')
            self.headers[cookie_output[0]] = cookie_output[1]

        return sid

    def getSessionVar(self, var):
        return RedisConnection.hget('session_' + self.getSession(), var) or None

    def setSessionVar(self, var, value):
        RedisConnection.hset('session_' + self.getSession(), var, value)

    def deleteSessionVar(self, var):
        RedisConnection.hdel('session_' + self.getSession(), [var])

    def getFile(self, content_type, base_dir, file_name):
        file_name = '%s/%s' % (base_dir, file_name)

        if (file_name and os.path.isfile(file_name)):
            content_type = read_mime_types(file_name)
            with open(file_name) as fh:
                return content_type, fh.read()
        else:
            return None, None
