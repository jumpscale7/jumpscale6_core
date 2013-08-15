from OpenWizzy import o

import OpenWizzy.core.system

##__all__ = ['PlatformType', 'AppStatusType', 'ErrorconditionLevel', 'LogLevel', 'MessageType', 'ActionStatus', 'SeverityType', 'AppStatusType', 'JobStatusType', 'REST']
from OpenWizzy.core.enumerators.PlatformType import PlatformType
##from OpenWizzy.core.enumerators.SeverityType import SeverityType
from OpenWizzy.core.enumerators.AppStatusType import AppStatusType
from OpenWizzy.core.enumerators.ErrorConditionLevel import ErrorConditionLevel
from OpenWizzy.core.enumerators.ErrorConditionType import ErrorConditionType
from OpenWizzy.core.enumerators.LogLevel import LogLevel
from OpenWizzy.core.enumerators.MessageType import MessageType

class Empty():
	pass

o.enumerators=Empty()

o.enumerators.PlatformType=PlatformType
o.enumerators.AppStatusType=AppStatusType
o.enumerators.ErrorConditionLevel=ErrorConditionLevel
o.enumerators.ErrorConditionType=ErrorConditionType
o.enumerators.LogLevel=LogLevel
o.enumerators.MessageType=MessageType


