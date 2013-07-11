from pylabs.InitBase import *
import os
import time

q.application.appname = "teststats"
q.application.start()

# print "* check app server started" #do this by  checking on ftp then we know for sure appserver also ok
# if q.system.net.waitConnectionTest("127.0.0.1",21,30)==False:
#     msg="could not start the ftpserver, check in corresponding tab in console."
#     raise RuntimeError(msg)
# print "* run simulation"


def test(name):
    return name

import inspect
import time

import ujson

import zmq.green as zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:4244")

#  Do 10 requests, waiting each time for a response
def client():
    for request in range(1,10):
        socket.send("Hello")
        message = socket.recv()
        print "Received reply ", request, "[", message, "]"


client()

q.application.stop()

import msgpack

import zerorpc
#client = zerorpc.Client()

import zerorpc

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")
print "start"
for i in range(10000):
    c.add_man("RPC")
print "stop"



from pylabs.Shell import ipshellDebug,ipshell
print "DEBUG NOW oo"
ipshell()

client.connect(endpoint)

class Job():
    def __init__(self, defname, \
            defcode,defmd5,defpath="",\
            defagentid="", \
            jname="", jcategory="", jerrordescr="",\
            jrecoverydescr="", jmaxtime=0, jsource="",\
            juser="", jwait=False,defargs={},executorrole=""):
        self.defname=defname
        self.defcode=defcode
        self.defmd5=defmd5
        self.defpath=defpath
        self.defargs=defargs
        self.defagentid=defagentid
        self.jname=jname
        self.jcategory=jcategory
        self.jerrordescr=jerrordescr
        self.jrecoverydescr=jrecoverydescr
        self.jmaxtime=jmaxtime
        self.jsource=jsource
        self.juser=juser
        self.jwait=jwait
        self.executorrole=executorrole

    def dumps(self):
        # return msgpack.dumps(self.__dict__)
        return ujson.dumps(self.__dict__)

    def loads(self,s):
        # self.__dict__.update(msgpack.loads(s))
        self.__dict__.update(ujson.loads(s))

    __str__=dumps
    __repr__=dumps
        

def perftest():
    print "start"
    nr=100000
    start=time.time()
    for i in range(0,nr):
        i=Job("name","sdsdsdsd sd sds ds ddddddddddddddddddddddddddddddddddddddd","dfsdfsdfsdfsdfsdfsdfsdfsdf","sdsadddddddddddddddddddddddddddddddddddddddddddddddddd","sddddddd")
        s=i.dumps()
        # ujson.loads(s)
        i.loads(s)
    stop=time.time()
    print "nrsec:%s" % str(float(nr)/(float(stop)-float(start)))
    print "stop"



class WorkerClient():
    def __init__(self):
        self.client=q.core.appserver6.getAppserverClient("127.0.0.1",9999,"1234")
        self.jobhandler=self.client.getActor("system","jobhandler",instance=0)


    def do(self,jfunction,jname="",executorrole="*",jcategory="",jerrordescr="",jrecoverydescr="",jmaxtime=0,\
        jsource="",juser="",jwait=True,**args):
        source=inspect.getsource(jfunction)
        md5=q.tools.hash.md5_string(source)
        filepath=inspect.getabsfile(jfunction)
        methodname=source.split("\n")[0].split("def")[1].split("(")[0].strip()
        source=source.replace(methodname,"jfunc")

        job=Job(defname=methodname, \
            defcode=source,defpath=filepath,\
            defagentid=q.application.whoAmI, \
            jname=jname, jcategory=jcategory, jerrordescr=jerrordescr,\
            jrecoverydescr=jerrordescr, jmaxtime=jmaxtime, jsource=jlocation,\
            wait=jwait,defmd5=md5,defargs=args,executorrole=executorrole).dumps()
        

perftest()

wc=WorkerClient()
print wc.do(test,name="hallo")

q.application.stop()
