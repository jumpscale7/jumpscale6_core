from JumpScale.core.errorhandling.ErrorConditionHandler import BaseException

class AuthenticationError(BaseException):
    pass

class MethodNotFoundException(BaseException):
    pass

class RemoteException(BaseException):
    pass
