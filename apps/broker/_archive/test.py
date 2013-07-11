from pylabs.InitBase import *
q.application.appname = "test"
q.application.start()
import time
q.qshellconfig.interactive=True

q.logger.addLogTargetClientDaemon()
q.logger.log("test")

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW ss"
ipshell()


start=time.time()
nr=100000
print "start perftest for %s"%nr
for i in range(nr):
    msg=q.logger.encodeLog(message="this si a message, hsds sdafsf asdf asdf adsf sdf asdf sd gs d", level=5, category='DFSDF.FSDF', tags='',job=0,parentjob=0,epoch=0)
    o=q.logger.decodeLogMessageToLogObject(msg)
stop=time.time()
nritems=nr/(stop-start)
print nritems
from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW uuu"
ipshell()

