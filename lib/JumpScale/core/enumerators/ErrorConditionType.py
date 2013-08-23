
from JumpScale.core.baseclasses import BaseEnumeration

class ErrorConditionType(BaseEnumeration):

    def __init__(self, level):
        self.level = level 
    
    def __int__(self):
        return self.level
    
    def __cmp__(self, other):
        return cmp(int(self), int(other))
    
    
ErrorConditionType.registerItem('UNKNOWN', 0)
ErrorConditionType.registerItem('BUG', 1)
ErrorConditionType.registerItem('OPERATIONS', 2)
ErrorConditionType.registerItem('MONITORING', 3)
ErrorConditionType.registerItem('PERFORMANCE', 4)
ErrorConditionType.registerItem('INPUT', 5)

ErrorConditionType.finishItemRegistration()

