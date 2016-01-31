import urllib2
import mimetypes
import tempfile
import os
import imghdr
import base64

from tuckshop.core.redis_connection import RedisConnection
from tuckshop.core.tuckshop_exception import TuckshopException


class Image(object):
    """Provides methods for obtaining and caching inventory images"""

    DEFAULT_IMAGE = 'http://www.monibazar.com/images/noimage.png'

    @property
    def cache_key(self):
        """Returns the redis key for cached image for the inventory object"""
        return 'Image_Data_%s' % self.inventory.id

    @property
    def mime_type_cache_key(self):
        return 'Image_Mime_%s' % self.inventory.id

    def __init__(self, inventory):
        """Sets up the object"""
        self.inventory = inventory

    def getImageUrl(self):
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
            image_file = Image.downloadImage(self.getImageUrl())

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

        return mime_type, image_data
