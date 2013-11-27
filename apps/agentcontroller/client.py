from JumpScale import j

import httplib
import thread
import time

import JumpScale.grid.geventws


j.application.start("agentcontrollertest")

j.logger.consoleloglevel = 2


client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user="admin", passwd="1234", \
    roles=["system.1", "hypervisor.1"],category="agent")


print client.listSessions()




print "start test"
for i in range(1):
    job=client.executeJumpscript("opencode","dummy","node",args={"msg":"amessage"},timeout=60,wait=True)
# resultcode,result=client.waitJumpscript(jobid)

if job["resultcode"]>0:
    eco= j.errorconditionhandler.getErrorConditionObject(ddict=job["result"])
    j.errorconditionhandler.processErrorConditionObject(eco)
else:
    print "result:%s"%job["result"]


j.application.stop()