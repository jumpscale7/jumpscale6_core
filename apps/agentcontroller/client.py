from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.agentcontroller

import sys

j.application.start("jumpscale:agentcontrollertest")
j.application.initGrid()

j.logger.consoleloglevel = 5



client=j.clients.agentcontroller.get("127.0.0.1")

# ac=client.get("127.0.0.1")

jpclient=j.clients.agentcontroller.getClientProxy(category="jpackages",agentControllerIP="127.0.0.1")

print jpclient.listJPackages(_agentid=1)

#job=client.execute("opencode","wait","node",msg="test:%s"%0,timeout=5,wait=True,lock="")
# jp= client.execute('jumpscale', 'error', 'node', timeout=10)
#jp= client.execute('jumpscale', 'jpackage_info', role="master", domain="jumpscale", pname="osis", version="1.0",timeout=10)

# print jp

j.application.stop()

print "start test"
for i in range(1):
    print i
    args={}
    args["msg"]="test"
    result=client.executeJumpScript(organization="jumpscale", name="echo", nid=j.application.whoAmI.nid, role=None, args=args, all=False, timeout=600, wait=True, queue='io', transporttimeout=5, _agentid=0)
    print result
    # job=client.execute(,,msg="test:%s"%i,timeout=5,wait=True,lock="")
    # job=client.waitJumpscript(job["id"])
    # print job



    # if job["resultcode"]>0:
    #     eco= j.errorconditionhandler.getErrorConditionObject(ddict=job["result"])
    #     j.errorconditionhandler.processErrorConditionObject(eco)
    # else:
    #     print "result:%s"%job["result"]

j.application.stop()

print "start test"
for i in range(1):
    job=client.execute("opencode","dummy","node",args={"msg":"amessage"},timeout=60,wait=True,lock="alock")
    from IPython import embed
    print "DEBUG NOW id"
    embed()
    
    resultcode,result=client.waitJumpscript(job.id)

if job["resultcode"]>0:
    eco= j.errorconditionhandler.getErrorConditionObject(ddict=job["result"])
    j.errorconditionhandler.processErrorConditionObject(eco)
else:
    print "result:%s"%job["result"]


