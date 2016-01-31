from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.page.page_base import PageBase
from tuckshop.page.not_found import NotFound
from tuckshop.app.models import Inventory


class ItemImage(PageBase):
    """Page class for handling static files"""

    REQUIRES_AUTHENTICATION = True
    PERMISSION = None
    NAME = None

    def __init__(self, request_handler):
        """Obtains the image object and image data"""
        super(ItemImage, self).__init__(request_handler)
        self.image_object = Inventory.objects.get(pk=self.get_item_id()).getImageObject()
        self.mime_type, self.image_data = self.image_object.getImage()

    @property
    def CONTENT_TYPE(self):
        """Returns the mime-type returned by the image"""
        return 'image/%s' % self.mime_type

    def getItemId(self):
        """Obtains the item ID from the URL"""
        if StaticFile.getUrlParts(self.request_handler)[2]:
            return int(StaticFile.getUrlParts(self.request_handler)[2])
        else:
            raise TuckshopException('Item ID not supplied')

    def processPage(self):
        """There is no processing requireed for the page"""
        pass

    def processPost(self):
        """There is no post action for this page"""
        pass

    def processTemplate(self):
        """Writes the image data to the request"""
        self.request_handler.wfile.write(self.image_data)
