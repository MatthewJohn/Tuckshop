from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound

class StaticFile(PageBase):
    """Page class for handling static files"""

    REQUIRES_AUTHENTICATION = False
    ADMIN_PAGE = False
    CONTENT_TYPE = None
    NAME = None

    @property
    def base_dir(self):
        return self.BASE_DIR

    def __init__(self, *args, **kwargs):
        super(StaticFile, self).__init__(*args, **kwargs)
        self.not_found_object = False

    def processPage(self):
        file_name = StaticFile.getUrlParts(self.request_handler)[2] if StaticFile.getUrlParts(self.request_handler)[2] else None
        self.file_content = None
        if file_name:
            mime_type, self.file_contents = self.getFile(self, self.base_dir, file_name)
            if not self.base_dir:
                self.CONTENT_TYPE = mime_type

        # If file name was not passed or file does not exist,
        # return a 404
        if not file_name or not self.file_contents:
            self.not_found_object = NotFound(self.request_handler)

    def processPost(self):
        pass

    def processHeaders(self):
        if self.not_found_object:
            self.not_found_object.processHeaders()
        else:
            super(StaticFile, self).processHeaders()

    def processTemplate(self):
        if self.not_found_object:
            self.not_found_object.processTemplate()
        else:          
            self.request_handler.wfile.write(self.file_contents)

class CSS(StaticFile):
    BASE_DIR = 'css'
    CONTENT_TYPE = 'text/css'

class JS(StaticFile):
    BASE_DIR = 'js'
    CONTENT_TYPE = 'text/javascript'

class Font(StaticFile):
    BASE_DIR = 'fonts'