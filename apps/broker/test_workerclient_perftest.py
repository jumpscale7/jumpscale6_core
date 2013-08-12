from OpenWizzy import o
import OpenWizzy.grid.grid

import time
import gevent
import sys

o.application.appname = "brokertest"
o.application.start()

o.core.grid.init()

def test(name,color):
    o.logger.log("this is test log of a job", level=3, category="a.msg")
    #raise RuntimeError("testerror")
    return name+" "+color


GeventLoop=o.core.gevent.getGeventLoopClass()

class WorkerClientTest(GeventLoop):

    def __init__(self,server="localhost",port=5555,instance=1,nrtests=1):
        GeventLoop.__init__(self)
        self.schedule("timer",self._timer)
        self.instance=instance
        self.client=o.core.grid.getZWorkerClient(ipaddr=server)
        # self.client=ZClient()
        self.nr=nrtests
        self.counter=0
        self.total=0
        self.laststart=time.time()        

    def report(self):
        self.counter=0
        self.laststart=time.time()
        while True:
            now=time.time()
            if float(now)-float(self.laststart)>0:
                print "nrsec:%s" % str(float(self.counter)/(float(now)-float(self.laststart)))
            self.laststart=now
            self.counter=0
            gevent.sleep(2)

    def start(self):
        #do only start when first connection done
        self.client.ping()

        print "start"
        self.schedule("report",self.report)
        while True: 
            self.counter+=1
            self.total+=1
            # result=self.client.ping()
            result=self.client.do(test,name="hallo",color="red")
            # print "result of remote exec:%s"%result
            if self.total>self.nr:
                break
        print "done"



if len(sys.argv)==5:
    addr=sys.argv[1] 
    port=int(sys.argv[2])
    instance=int(sys.argv[3])
    nrtests=int(sys.argv[4])
elif len(sys.argv)==1:
    addr="127.0.0.1"
    port=5555
    instance=1
    nrtests=1000
else:
    raise RuntimeError("Format needs to be: 'python zclientest.py localhost 5555 1 1000'")


testclient=WorkerClientTest(addr,port,instance,nrtests)
testclient.start()

o.application.stop()
