from pylabs.InitBase import *

import time

from ZClient import *

q.application.appname = "brokertest"
q.application.start()

def test(name,color):
    return name+color

from GeventLoop import GeventLoop

class Test():

    def __init__(self):
        self.i=0
        self.client=ZClient()
        self.nr=1

    def start(self):
        result=self.client.ping()
        start=time.time()
        for self.i in range(self.nr):
            # result=self.client.do(test,name="hallo",color="red")
            result=self.client.ping()
        print "stop"
        stop=time.time()
        print "nrsec:%s" % str(float(self.nr)/(float(stop)-float(start)))

        print "result of do was:%s"%result

        self.client.stopbroker()


test=Test()
test.nr=10000
test.start()

q.application.stop()