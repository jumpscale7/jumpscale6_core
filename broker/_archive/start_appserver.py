import time
from pylabs.InitBase import *    

q.application.appname = "GreenBoatsWS"
q.application.start()

q.qshellconfig.interactive=True
q.logger.disable()

q.manage.appserver6.startprocess()
    

q.application.stop()
