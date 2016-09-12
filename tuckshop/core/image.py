import urllib2
import mimetypes
import tempfile
import os
import PIL.Image
import imghdr
import base64
import StringIO

from tuckshop.core.redis_connection import RedisConnection
from tuckshop.core.tuckshop_exception import TuckshopException


class Image(object):
    """Provides methods for obtaining and caching inventory images"""

    DEFAULT_IMAGE = 'http://www.irishdist.ie/wp-content/uploads/2015/07/noimage-400x400.jpg'

    @property
    def cache_key(self):
        """Returns the redis key for cached image for the inventory object"""
        return 'Image_Data_%s' % self.inventory.id

    @property
    def mime_type_cache_key(self):
        return 'Image_Mime_%s' % self.inventory.id

    @property
    def resized_cache_key(self):
        return 'Image_Thumbnail_%s' % self.inventory.id

    def __init__(self, inventory):
        """Sets up the object"""
        self.inventory = inventory

    def _getImageUrl(self):
        # Return the image URL, if it exists. Else, return a default image
        return self.inventory.image_url if self.inventory.image_url else self.DEFAULT_IMAGE

    def getSrc(self):
        """Returns the html 'src' data for the image"""
        mime_type, image_data = self.getImage()
        image_data = base64.b64encode(image_data)
        return 'data:image/%s;base64,%s' % (mime_type, image_data)

    @staticmethod
    def downloadImage(url):
        """Attempts to open the image url"""
        try:
            image_file = urllib2.urlopen(url)
        except:
            return None

        # If the return code is not 200 - OK, return None
        if image_file.getcode() != 200:
            return None
        return image_file

    def getImage(self, refresh_cache=False):
        """Obtains and returns the image data for the
           object"""
        if (not RedisConnection.exists(self.cache_key) or
                not RedisConnection.exists(self.mime_type_cache_key) or
                refresh_cache):
            # Download image
            image_file = Image.downloadImage(self._getImageUrl())

            if not image_file:
                image_file = Image.downloadImage(self.DEFAULT_IMAGE)

            if not image_file:
                raise TuckshopException('Could not obtain image for %s or default image' % self.inventory.id)

            image_data = image_file.read()

            # Create temp file to obtain mime-type
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
            temp_file_path = temp_file.name
            temp_file.write(image_data)
            temp_file.close()
            mime_type = imghdr.what(temp_file_path)
            os.unlink(temp_file_path)

            # If the mime-type of the image was recognised,
            # store the image in the redis database
            if mime_type:
                RedisConnection.set(self.cache_key, image_data)
                RedisConnection.set(self.mime_type_cache_key, mime_type)
        else:
            image_data = RedisConnection.get(self.cache_key)
            mime_type = RedisConnection.get(self.mime_type_cache_key)

        if not RedisConnection.exists(self.resized_cache_key) or refresh_cache:
            # Define thumbnail image size
            size = (150, 150)

            # Open image using PIL and resize
            image = PIL.Image.open(StringIO.StringIO(image_data))
            image.thumbnail(size, PIL.Image.ANTIALIAS)

            # Create transaprent background to put the image on
            background = PIL.Image.new('RGBA', size, (255, 255, 255, 0))
            background.paste(image, ((size[0] - image.size[0]) / 2, (size[1] - image.size[1]) / 2))

            # Fake filehandler and filename, so that the extension can be the same as the origin MIME type
            output = StringIO.StringIO()
            output.name = 'test.%s' % mime_type
            background.save(output)

            # Get value of StringIO object to save/return
            image_data = output.getvalue()

            # Close StringIO object
            output.close()

            # Update resized image in database
            RedisConnection.set(self.resized_cache_key, image_data)
        else:
            image_data = RedisConnection.get(self.resized_cache_key)

        # Return the mime-type and image_data
        return mime_type, image_data

    def getImageUrl(self):
        """Returns an absolute URL for the image"""
        return '/item-image/%s' % self.inventory.id
