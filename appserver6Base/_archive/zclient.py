import sys
import zmq

import ujson

from pylabs.InitBase import *
from ZJob import *
import os
import time


q.application.appname = "testworker"
q.application.start()
context = zmq.Context(1)


class WorkerClient():
    def __init__(self,server="tcp://localhost:5555"):
        self.serverEndpoint=server
        self.requestRetries= 300
        self.retries_left =self.requestRetries 
        self.requestTimeout=10000

        print "I: Connecting to server"
        self.client = context.socket(zmq.REQ)
        # identity = "cl1"
        # self.client.setsockopt(zmq.IDENTITY, identity)
        self.client.connect(self.serverEndpoint)

        self.poll = zmq.Poller()
        self.poll.register(self.client, zmq.POLLIN)

        res=self.register(1,1,["test"])
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW jjj"
        ipshell()
        


    def send(self,msg):

        while self.retries_left:

            # print "I: Sending (%s)" % msg            
            self.client.send(msg)

            expect_reply = True
            while expect_reply:
                socks = dict(self.poll.poll(self.requestTimeout))
                if socks.get(self.client) == zmq.POLLIN:
                    reply = self.client.recv()                    
                    if not reply:
                        break
                    else:
                        # print "I: Server replied OK (%s)" % reply
                        retries_left = self.requestRetries
                        expect_reply = False
                        return reply

                else:
                    print "W: No response from server, retrying"
                    # Socket is confused. Close and remove it.
                    self.client.setsockopt(zmq.LINGER, 0)
                    self.client.close()
                    self.poll.unregister(self.client)
                    self.retries_left -= 1
                    if self.retries_left == 0:
                        print "E: Server seems to be offline, abandoning"
                        break
                    print "I: Reconnecting and resending (%s)" % msg
                    # Create new connection
                    self.client = context.socket(zmq.REQ)
                    self.client.connect(self.serverEndpoint)
                    self.poll.register(self.client, zmq.POLLIN)
                    self.client.send(msg)


    def do(self,jfunction,jname="",executorrole="*",jcategory="",jerrordescr="",jrecoverydescr="",jmaxtime=0,\
        jsource="",juser="",jwait=True,**args):
        source=inspect.getsource(jfunction)
        md5=q.tools.hash.md5_string(source)
        filepath=inspect.getabsfile(jfunction)
        methodname=source.split("\n")[0].split("def")[1].split("(")[0].strip()
        source=source.replace(methodname,"jfunc")

        job=ZJob(defname=methodname, \
            defcode=source,defpath=filepath,\
            defagentid=q.application.whoAmI, \
            jname=jname, jcategory=jcategory, jerrordescr=jerrordescr,\
            jrecoverydescr=jerrordescr, jmaxtime=jmaxtime, jsource=jsource,\
            jwait=jwait,defmd5=md5,defargs=args,executorrole=executorrole)

        job.guid=q.base.idgenerator.generateGUID()
        result=ujson.loads(self.send(job.dumps()))
        return result["jresult"]

    def _sendcmd(self,cmd,**args):
        zrpc=ZRPC()
        zrpc.cmd=cmd
        zrpc.args=args
        result=ujson.loads(self.send(zrpc.dumps()))

        if result["state"]=="ok":
            return result["result"]
        else:
            raise RuntimeError("error in send cmd:%s, %s"%(cmd,result["result"]))

    def getactivejobs(self):
        return self._sendcmd("getactivejobs")

    def ping(self):
        return self._sendcmd("ping")  




        
import inspect

def test(name):
    return name

import time

wc=WorkerClient()

print "start"
nr=10000
start=time.time()
for i in range(nr):
    # wc.do(test,name="hallo")
    wc.ping()
print "stop"
stop=time.time()
print "nrsec:%s" % str(float(nr)/(float(stop)-float(start)))

q.application.stop()

context.term()