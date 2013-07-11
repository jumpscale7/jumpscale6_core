import time
import gevent
import zmq.green as zmq

class GeventLoop():
    def __init__(self):
        self.greenlets = {}
        self.now=0


    def _timer(self):
        """
        will remember time every 1 sec
        """
        #lfmid = 0

        while True:
            self.now = int(time.time())
            # if lfmid<self.epoch-200:
            #     lfmid=self.epoch
            #     self.fiveMinuteId=o.base.time.get5MinuteId(self.epoch)
            #     self.hourId=o.base.time.getHourId(self.epoch)
            #     self.dayId=o.base.time.getDayId(self.epoch)
            # print "timer"
            gevent.sleep(1)


    def schedule(self, name, ffunction, **args):
        self.greenlets[name] = gevent.greenlet.Greenlet(ffunction, **args)
        self.greenlets[name].start()
        return self.greenlets[name]

    def start(self):
        """
        """
        self.startClock()
        #print "start"
        while True:
            gevent.sleep(100)        

    def startClock(self):
        self.schedule("timer", self._timer)


