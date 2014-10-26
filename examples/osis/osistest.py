from JumpScale import j

j.application.start("osistest")
import JumpScale.grid.osis

# cl=j.core.osis.getOsisModelClass("test_complextype","project")

import time

client = j.core.osis.getClientByInstance('main')


def testHB():

    clienthb=j.core.osis.getClientForCategory(client,"system","heartbeat")
    o=clienthb.new()

    clienthb.set(o,waitIndex=True)

    o2=clienthb.get(o.guid)

    assert(o2==o)

    o2=clienthb.delete(o.guid)

    time.sleep(1)

    assert clienthb.exists(o.guid)==False


# testHB()



# getNameIDsInfo

def testeco():
    clienteco=j.core.osis.getClientForCategory(client,"system","eco")
    o=clienteco.new()

    clienteco.set(o,waitIndex=True)

    o2=clienteco.get(o.guid)

    o2=clienteco.delete(o.guid)

    time.sleep(0.5)

    assert clienteco.exists(o.guid)==False

# testeco()

def testinfo():
    clienteco=j.core.osis.getClientForCategory(client,"system","info")
    o=clienteco.new(category="etc.nginx.main",content="fake")

    clienteco.set(o,waitIndex=True)

    o2=clienteco.get(o.guid)


# testinfo()
    


def testSet(client):
    for i in range(10):
        obj = client.new()
        obj.name="test%s" % i
        obj.machineguid="guid_%s"%i
        key, new, changed = client.set(obj.guid,obj,waitIndex=True)

    obj = client.get(key),

    print obj

    return obj

# print client.listNamespaces()

# clientnode=j.core.osis.getClientForCategory(client,"system","node")

# clientvfs=j.core.osis.getClientForCategory(client,"osismodel","vfs")
# vfs=clientvfs.new()

# obj=testSet(clientnode)


j.application.stop()

#@todo (P2) create test suite on znode (auto tests)
#@todo (P2) patch pyelasticsearch to work well in gevent so it does not block (monkey patching of socket)
#@todo (P2) patch & check osisclient to work non blocking when in gevent
#@todo (P3) put arakoon as backend (in stead of filesystem db)
#@todo (P3) refactor arakoon client to have nice config files in hrd format (see osis dir)
