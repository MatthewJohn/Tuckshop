
from enum import Enum

class Permission(Enum):
    ADMIN = 0
    FLOAT_ACCESS = 1
    REVIEW_SHARED_ACCOUNTS = 2

    @staticmethod
    def getDict(return_value):
        dictionary = {}
        for name, member in Permission.__members__.items():
            dictionary[name] = member.value if return_value else member
        return dictionary
