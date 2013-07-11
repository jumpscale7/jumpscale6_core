import sys
import ujson
from pylabs.InitBase import *
import os

import time
import gevent
import zmq.green as zmq
from gevent.event import AsyncResult

from ZObjects import *
from ZClient import *

q.application.appname = "testworker"
q.application.start()


def test(name,color):
    return name+color

# import time

# wc=ZClient()


class DataProcessorClient():
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PAIR)
        # socket.connect("ipc:///tmp/feeds/0")
        self.socket.connect("tcp://localhost:%s" % 7788)

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        oo2=ZAction(name="asda sdasdas",code="asdasd asda sd asd asd asd asd asd as d",path="asda sd asda sd asd asd ",category="asd asd asd as", errordescr="asd asd asd asd asd ",\
            recoverydescr="dsfsadfgsdsdfgsdfgsdfgs", maxtime=45,masterid=453)

        self.ooo=q.db.serializers.ujson.dumps(oo2)
        
        self.watchdog = AsyncResult()



    def _timer(self):
        """
        will remember time every 0.5 sec
        """
        lfmid=0        
        while True:
            self.epoch=int(time.time())            
            if lfmid<self.epoch-200:
                lfmid=self.epoch
                # self.fiveMinuteId=q.base.time.get5MinuteId(self.epoch)
                self.hourId=q.base.time.getHourId(self.epoch)
                # self.dayId=q.base.time.getDayId(self.epoch)
            gevent.sleep(0.5)

    def returnok(self):
        """
        will every 5 sec go back to sender to acknowledge succesfull processed items
        """     
        while True:
            socks = dict(self.poller.poll(1))
            print "checkok"
            if socks.get(self.socket) == zmq.POLLIN:
                msg=self.socket.recv()
                print "received:%s"%msg
                self.watchdog.set(int(msg))
                self.watchdog=AsyncResult()
            else:             
                print "timeout on return ok"
            gevent.sleep(5)            

    def start(self):

        print "start"

        TIMER=gevent.greenlet.Greenlet(self._timer)
        TIMER.start()

        RETURNOK=gevent.greenlet.Greenlet(self.returnok)
        RETURNOK.start()

        self.main()  

    def send(self,i,msg):
        self.socket.send(msg)
        while self.watchdog.get()<i:
            gevent.sleep(1)
            pass
        
    def main(self):

        nr=100000
        start=time.time()
        for i in range(nr/1000):
            # wc.do(test,name="hallo",color="red")
            # wc.ping()
            # ooo=q.db.serializers.msgpack.dumps(oo2)
            
            # ooo=q.db.serializers.snappy.dumps(ooo)
            #ooo=q.db.serializers.blosc.dumps(ooo)
            for i2 in range(100):
                gevent.spawn(self.send,i*1000+i2,self.ooo)
            gevent.sleep(0)
            
            print i*1000

        self.socket.send("***")
        print "stop"
        stop=time.time()
        print "nrsec:%s" % str(float(nr)/(float(stop)-float(start)))


dp=DataProcessorClient()
dp.start()

q.application.stop()