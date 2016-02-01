"""Contains class for permissions page"""

from tuckshop.page.page_base import VariableVerificationTypes
from tuckshop.page.admin.admin_base import AdminBase
from tuckshop.core.tuckshop_exception import TuckshopException
from tuckshop.app.models import User
from tuckshop.core.permission import Permission as PermissionObj


class Permission(AdminBase):

    NAME = 'Permissions'
    TEMPLATE = 'permission'
    REQUIRES_AUTHENTICATION = True
    PERMISSION = PermissionObj.ADMIN
    URL = '/permission'
    SUB_MENU_ORDER = 2
    SUB_MENU = AdminBase

    def processPage(self):
        self.return_vars['users'] = User.objects.filter(shared=False).order_by('uid')
        self.return_vars['permissions'] = PermissionObj.getDict(return_value=False)

    def processPost(self):
        permissions = {}
        user_object = User.objects.get(uid=self.getPostVariable(name='uid', var_type=str))
        for permission in PermissionObj.getDict(return_value=False):
            permission_value = self.getPostVariable(name=permission, var_type=bool, default=False, set_default=True)
            if permission == 'ADMIN':
                if permission_value:
                    user_object.setAdmin()
                else:
                    user_object.removeAdmin()
            else:
                if permission_value:
                    user_object.addPermission(PermissionObj[permission])
                else:
                    user_object.removePermission(PermissionObj[permission])
            
