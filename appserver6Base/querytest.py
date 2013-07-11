import time

from pprint import pprint
import cProfile
import pstats

from pylabs.InitBase import *
    
q.application.appname = "querytest"
q.application.start()

q.qshellconfig.interactive=True
    
q.core.appserver6.loadActorsInProcess()

lh=q.apps.acloudops.actionlogger.extensions.loghandler
lh.loadTypes()

es=q.clients.elasticsearch.get()

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW "
ipshell()


q.application.stop()
