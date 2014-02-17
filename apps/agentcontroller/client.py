from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.agentcontroller

import sys

j.application.start("jumpscale:agentcontrollertest")
j.application.initGrid()

j.logger.consoleloglevel = 5



client=j.clients.agentcontroller

#job=client.execute("opencode","wait","node",msg="test:%s"%0,timeout=5,wait=True,lock="")
jp= client.execute('jumpscale', 'error', 'node', timeout=10)
#jp= client.execute('jumpscale', 'jpackage_info', role="master", domain="jumpscale", pname="osis", version="1.0",timeout=10)

print jp

j.application.stop()

print "start test"
for i in range(10):
    print i
    job=client.execute("opencode","wait","node",msg="test:%s"%i,timeout=5,wait=True,lock="")
    # job=client.waitJumpscript(job["id"])
    print job



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


