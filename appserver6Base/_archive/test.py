import time

from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *

q.application.appname = "loadlogtest"
q.application.start()

q.qshellconfig.interactive=True

q.core.appserver6.loadActorsInProcess()

#lhandler=q.apps.acloudops.actionlogger.extensions.loghandler

#q.core.osis.destroy("acloudops") #remove all existing objects & indexes

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW test main"
ipshell()


q.application.stop()
