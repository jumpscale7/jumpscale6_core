from pylabs.InitBase import *


q.application.appname = "brokerclient"
q.application.start()

q.core.grid.init()

#getNameIDsInfo

# eco=q.errorconditionhandler.getErrorConditionObject(msg="this is error",msgpub="pubmessage",category="a.cat")
# client.set("system","errorcondition",eco,key=eco.guid)
# print client.get("system","errorcondition",eco.guid)

def testSet():
    for i in range(10):
        obj=q.core.grid.zobjects.getZNodeObject(name="test%s"%i)
        key,new,changed=client.set("system","znode",obj)

    obj=client.get("system","znode",key)

    print obj

# namespacename=client.createNamespace(name="broker_",forCoreObjects=True,incrementName=True)
# client.listNamespaces()

from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW brokerclient"
ipshell()

q.application.stop()

#@todo (P1) test full working behaviour on znode object
#@todo (P1) implement query, list, ...
#@todo (P2) create test suite on znode (auto tests)
#@todo (P2) patch pyelasticsearch to work well in gevent so it does not block (monkey patching of socket)
#@todo (P2) patch & check osisclient to work non blocking when in gevent
#@todo (P3) put arakoon as backend (in stead of filesystem db)
#@todo (P3) refactor arakoon client to have nice config files in hrd format (see osis dir)
