from OpenWizzy import o
import OpenWizzy.baselib.taskletengine

# import zmq
import gevent
import time
# import gevent.monkey
# import zmq.green as zmq
from gevent import queue as queue
from ZDaemon import ZDaemon

class ZLoggerCMDS():
    def __init__(self, daemon):
        self.daemon = daemon

    def test(self):
        return "pong"

class Dummy():
    pass

class ZLogger(ZDaemon):

    def __init__(self, port=4444):
        ZDaemon.__init__(self,port=port,name="logger")
        self.addCMDsInterface(ZLoggerCMDS)
        self.init()

    def init(self):

        if o.system.fs.exists(path="cfg"):
            self.hrd=o.core.hrd.getHRDTree("cfg")
        else:
            self.hrd=None

        o.core.grid.logger=Dummy()

        path = "loghandling"
        if o.system.fs.exists(path=path):
            self.loghandlingTE = o.core.taskletengine.get(path)
            path = "loghandlingbatched"
            self.loghandlingBatchedTE = o.core.taskletengine.get(path)
            o.core.grid.logger.elasticsearch= None
            if self.hrd.getInt("logger.elasticsearch.enable")==1:
                o.core.grid.logger.elasticsearch = o.core.grid.getLogTargetElasticSearch(serverip=self.hrd.get("logger.elasticsearch.ip"))
            o.core.grid.logger.osis=None
            if self.hrd.getInt("logger.osis.enable")==1:
                o.core.grid.logger.osis=o.core.osis.getClientForCategory("logger", "log", ipaddr=self.hrd.get("logger.osis.ip"), port=self.hrd.getInt("logger.osis.port"))
        else:
            self.loghandlingTE = None

        path = "eventhandling"
        if o.system.fs.exists(path=path):
            self.eventhandlingTE = o.core.taskletengine.get(path)
            self.eventsMemLog = {}
            if self.hrd.getInt("logger.osis.enable")==1:
                o.core.grid._loadConfig()
                bid=o.core.grid.config.getInt("grid.broker.id")
                counter=1
                stop=False
                while bid==0 and stop==False:
                    bid=o.core.grid.config.getInt("grid.broker.id")
                    counter+=1
                    time.sleep(1)
                    o.core.grid._loadConfig()
                    print "wait for identification of broker id, comes from 'grid.broker.id' in hrd config for node."
                    if counter>30:                        
                        stop=True
                if bid==0:                    
                    o.errorconditionhandler.raiseBug(message="grid.broker.id cannot be 0 when starting logger",category="grid.init")
                o.core.grid.logger.osiseco=o.core.osis.getClientForCategory("broker_%s"%bid, "eco", ipaddr=self.hrd.get("logger.osis.ip"), port=self.hrd.getInt("logger.osis.port"))
        else:
            self.eventhandlingTE = None


        self.logQueue = queue.JoinableQueue()
        self.eventQueue = queue.JoinableQueue()

        self.schedule("logGreenlet", self.logGreenlet)

        self.ids = {}
    
    
    def logGreenlet(self):
        batch = []
        queuesize = -1
        while True:
            gevent.sleep(0.1)
            i = 0
            while i < 500 and self.logQueue.empty() == False:
                msg = self.logQueue.get()
                if self.loghandlingTE != None:
                    obj=o.logger.getLogObjectFromDict(o.db.serializers.ujson.loads(msg))
                    if int(obj.order)==0:
                        key = "%s_%s_%s"%(obj.gid, obj.bid, obj.pid)
                        if key not in self.ids:
                            self.ids[key] = 0
                        self.ids[key] += 1
                        obj.order = self.ids[key]
                    if obj.epoch==0:
                        obj.epoch=self.now                    
                    obj = self.loghandlingTE.executeV2(logobj=obj)
                    if obj<>None:
                        batch.append(obj.__dict__)
                i += 1
            if batch != []:
                self.loghandlingBatchedTE.executeV2(logbatch=batch)
                batch = []
            #FOR DEBUG PURPOSES:
            newqueuesize = self.logQueue.qsize()
            if newqueuesize != queuesize:
                print "Queuesize: %s" % newqueuesize
                queuesize = newqueuesize

