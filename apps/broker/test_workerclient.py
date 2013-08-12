from OpenWizzy import o
import OpenWizzy.grid.grid

import time
import gevent
import sys

o.application.appname = "brokertest"
o.application.start()

o.core.grid.init()

def test(name,color):
    o.logger.log("this is test log of a job", level=3, category="a.cat")
    #raise RuntimeError("testerror")
    return name+" "+color

client=o.core.grid.getZWorkerClient(ipaddr="127.0.0.1")

result1=client.do(test,name="hallo",color="red",executorrole="worker.1")
for i in range(10):
    result2=client.do(test,name="hallo",color="red",executorrole="*")

print "agent1 executed%s"%result1



o.application.stop()
