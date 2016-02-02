"""Contains base class for admin pages"""

from tuckshop.page.page_base import PageBase
from tuckshop.core.permission import Permission

class AdminBase(PageBase):
    """Class for displaying a history page"""

    REQUIRES_AUTHENTICATION = True
    PERMISSION = Permission.ADMIN
