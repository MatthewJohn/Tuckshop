import cgi

from tuckshop.core.config import TOTAL_PAGE_DISPLAY

class PageBase(object):

    def __init__(self, request_handler):
        self.request_handler = request_handler
        self.post_vars = {
            'error': None,
            'warning': None,
            'info': None
        }

    @property
    def name(self):
        if self.NAME:
            return self.NAME
        else:
          raise NotImplementedError

    @property
    def template(self):
        if self.TEMPLATE:
            return self.TEMPLATE
        else:
            raise NotImplementedError

    def checkAuthentication(self):
        raise NotImplementedError

    def doGet(self):
        self.processPage()

    def doPost(self):
        self.processPost()
        self.processPage()

    def getPageData(self, current_page, total_pages, url_template):
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
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type']})

        variables = {}
        for field in form.keys():
            variables[field] = form[field].value
        return variables

    def getSession(self, send_header=False, clear_cookie=False):
        cookie = Cookie.SimpleCookie()
        sid = None
        if ('Cookie' in self.headers):
            cookie.load(self.headers.getheader('Cookie'))
            if ('sid' in cookie and cookie['sid']):
                sid = cookie['sid'].value

        if (not sid):
            sid = sha.new(repr(time.time())).hexdigest()
            cookie['sid'] = sid
            cookie['sid']['expires'] = 24 * 60 * 60
            if (send_header):
                self.send_header('Set-Cookie', cookie.output())

        if (clear_cookie):
            RedisConnection.delete('session_' + self.getSession())
            cookie['sid'] = None
            self.send_header('Set-Cookie', cookie.output())

        return sid

    def getSessionVar(self, var):
        return RedisConnection.hget('session_' + self.getSession(), var) or None

    def setSessionVar(self, var, value):
        RedisConnection.hset('session_' + self.getSession(), var, value)

    def getFile(self, content_type, base_dir, file_name):
        file_name = '%s/%s' % (base_dir, file_name)

        if (file_name and os.path.isfile(file_name)):
            if content_type is None:
                content_type = read_mime_types(file_name)
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(self.includeFile(file_name))
        else:
            self.send_response(401)

    def includeFile(self, file_name):
        if (file_name and os.path.isfile(file_name)):
            with open(file_name) as fh:
                return fh.read()
        else:
            return None
