import time
from pylabs.InitBase import *

q.application.appname = "appserver6_client"
q.application.start()

client = q.core.appserver6.getAppserverClient("127.0.0.1", 9999, "1234")
system = client.getActor("system", "master", instance=0)


from pylabs.Shell import ipshell
print "DEBUG NOW main"
ipshell()


q.application.stop()
