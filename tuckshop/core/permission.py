
from enum import Enum

class Permission(Enum):
    ADMIN = 0
    FLOAT_ACCESS = 1
    REVIEW_SHARED_ACCOUNTS = 2
    ACCESS_TOUCH_VIEW = 3
    ACCESS_CREDIT_PAGE = 4
    ACCESS_STOCK_PAGE = 5

    @staticmethod
    def getDict(return_value):
        dictionary = {}
        for name, member in Permission.__members__.items():
            dictionary[name] = member.value if return_value else member
        return dictionary

    @staticmethod
    def get_default_permission():
        return [Permission.ACCESS_CREDIT_PAGE, Permission.ACCESS_STOCK_PAGE]
