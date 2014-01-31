from JumpScale import j

j.application.start("osisclient")
j.application.initGrid()
import JumpScale.grid.osis

cl=j.core.osis.getOsisModelClass("test_complextype","project")

from IPython import embed
print "DEBUG NOW uiuiui"
embed()


client = j.core.osis.getClient(user='root')
# getNameIDsInfo

# eco=q.errorconditionhandler.getErrorConditionObject(msg="this is error",msgpub="pubmessage",category="a.cat")
# client.set("system","errorcondition",eco,key=eco.guid)
# print client.get("system","errorcondition",eco.guid)


def testSet(client):
    for i in range(10):
        obj = client.new()
        obj.name="test%s" % i
        obj.machineguid="guid_%s"%i
        key, new, changed = client.set(obj)

    obj = client.get(key)

    print obj

    return obj

print client.listNamespaces()

# clientnode=j.core.osis.getClientForCategory(client,"system","node")

clientvfs=j.core.osis.getClientForCategory(client,"osismodel","vfs")
vfs=clientvfs.new()

# obj=testSet(clientnode)



from IPython import embed
print "DEBUG NOW main in test script osis"
embed()



j.application.stop()

#@todo (P2) create test suite on znode (auto tests)
#@todo (P2) patch pyelasticsearch to work well in gevent so it does not block (monkey patching of socket)
#@todo (P2) patch & check osisclient to work non blocking when in gevent
#@todo (P3) put arakoon as backend (in stead of filesystem db)
#@todo (P3) refactor arakoon client to have nice config files in hrd format (see osis dir)
