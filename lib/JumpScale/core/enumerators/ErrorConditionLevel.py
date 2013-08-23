
from JumpScale.core.baseclasses import BaseEnumeration

class ErrorConditionLevel(BaseEnumeration):
    """
    Iterrator for levels of errorconditions
    1: critical
    2: warning
    3: info
    """
    
    def __init__(self, level):
        self.level = level

    def __int__(self):
        return self.level
    
    def __cmp__(self, other):
        return cmp(int(self), int(other))


ErrorConditionLevel.registerItem('unknown', 0)
ErrorConditionLevel.registerItem('critical', 1)
ErrorConditionLevel.registerItem('warning', 2)
ErrorConditionLevel.registerItem('info', 3)

ErrorConditionLevel.finishItemRegistration()

