from OpenWizzy import o
from OpenWizzy.core.baseclasses import BaseEnumeration


IN_DEBUG_MODE = o.application.shellconfig.debug


def printInDebugMode(message):
    '''
    Prints a message only when Qshell is running in debug mode.

    @param message: message to print
    @type message: str
    '''

    #if IN_DEBUG_MODE:
    print(message)

if hasattr(q, 'enumerators') and not hasattr(o.enumerators, 'UjumbeMessageType'):
    class MessageServerMessageType(BaseEnumeration):
        def __cmp__(self, other):
            return cmp(int(self), int(other))

        def __init__(self, level):
            self.level = level

        def __int__(self):
            return self.level

        def __repr__(self):
            return str(self)

        @classmethod
        def _initItems(cls):
            cls.registerItem('error', 1)
            cls.registerItem('log', 2)
            cls.registerItem('signal', 3)
            cls.registerItem('status', 4)
            cls.finishItemRegistration()
