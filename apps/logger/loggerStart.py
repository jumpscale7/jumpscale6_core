from pylabs.InitBase import *


q.application.appname = "logger"
q.application.start()

q.core.grid.startLocalLogger()


q.application.stop()
