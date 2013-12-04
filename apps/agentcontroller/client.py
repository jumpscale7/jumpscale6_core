from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.geventws

import sys

j.application.start("agentcontrollertest")

j.logger.consoleloglevel = 5

client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234", \
    roles=["system.1", "hypervisor.1"],category="agent")

# print client.listSessions()

print "start test"
for i in range(10):
    print i
    job=client.executeJumpscript("opencode","wait","node",args={"msg":"test:%s"%i},timeout=60,wait=False,lock="test")
    job=client.waitJumpscript(job["id"])
    print job



    # if job["resultcode"]>0:
    #     eco= j.errorconditionhandler.getErrorConditionObject(ddict=job["result"])
    #     j.errorconditionhandler.processErrorConditionObject(eco)
    # else:
    #     print "result:%s"%job["result"]

j.application.stop()

print "start test"
for i in range(1):
    job=client.executeJumpscript("opencode","dummy","node",args={"msg":"amessage"},timeout=60,wait=True,lock="alock")
    from IPython import embed
    print "DEBUG NOW id"
    embed()
    
    resultcode,result=client.waitJumpscript(job.id)

if job["resultcode"]>0:
    eco= j.errorconditionhandler.getErrorConditionObject(ddict=job["result"])
    j.errorconditionhandler.processErrorConditionObject(eco)
else:
    print "result:%s"%job["result"]


