from JumpScale import j
import JumpScale.baselib.taskletengine

# import zmq
import gevent
import time
# import gevent.monkey
# import zmq.green as zmq
from gevent import queue as queue
from ..zdaemon.ZDaemon import ZDaemon

import JumpScale.grid.osis

class ZLoggerCMDS(object):

    def __init__(self, daemon):
        self.daemon = daemon
        self.logger = daemon.logger

    def logeco(self, eco, session):
        """
        log eco object (as dict)
        """
        eco["epoch"] = time.time()
        eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.logger.eventhandlingTE.executeV2(eco=eco, history=self.logger.eventsMemLog)

    def log(self, log, session):
        log = j.logger.getLogObjectFromDict(log)
        log=self.logger.loghandlingTE.executeV2(logobj=log,logger=self.daemon.logger)

    def logbatch(self, localegbatch, session):
        self.logger.loghandlingBatchedTE.executeV2(logbatch=logbatch)


class Dummy():
    pass


class ZLogger(ZDaemon):

    def __init__(self, port=4443):
        ZDaemon.__init__(self, port=port, name="logger")
        self.daemon.logger = self
        self.setCMDsInterface(ZLoggerCMDS, category='logger')
        self.init()

    def init(self):

        if j.system.fs.exists(path="cfg"):
            self.hrd = j.core.hrd.getHRD("cfg")
        else:
            self.hrd = None

        j.core.grid.logger = Dummy()

        j.application.initGrid()

        #OSIS INit
        OSISclient = j.core.osis.getClient()

        #make sure system namespace exists
        # OSISclient.createNamespace(name="system",template="coreobjects",incrementName=False)

        OSISclientLogger=j.core.osis.getClientForCategory(OSISclient,"logger","log")
        OSISclientEco=j.core.osis.getClientForCategory(OSISclient,"system","eco")

        path = "loghandling"
        if j.system.fs.exists(path=path):
            self.loghandlingTE = j.core.taskletengine.get(path)
            path = "loghandlingbatched"
            self.loghandlingBatchedTE = j.core.taskletengine.get(path)
            j.core.grid.logger.elasticsearch = None
            j.core.grid.logger.osis = OSISclientLogger
        else:
            self.loghandlingTE = None

        path = "eventhandling"
        if j.system.fs.exists(path=path):
            self.eventhandlingTE = j.core.taskletengine.get(path)
            self.eventsMemLog = {}
            j.core.grid.logger.osiseco = OSISclientEco
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
                obj = self.logQueue.get()
                                                
                if int(obj.order) == 0:
                    key = "%s_%s" % (obj.gid, obj.pid)
                    if key not in self.ids:
                        self.ids[key] = 0
                    self.ids[key] += 1
                    obj.order = self.ids[key]
                if obj.epoch == 0:
                    obj.epoch = self.now
                # obj = self.loghandlingTE.executeV2(logobj=obj)
                # if obj <> None:
                batch.append(obj.__dict__)

                i += 1
            if batch != []:
                self.loghandlingBatchedTE.executeV2(logbatch=batch)
                batch = []

            # # FOR DEBUG PURPOSES:
            # newqueuesize = self.logQueue.qsize()
            # if newqueuesize != queuesize:
            #     print "Queuesize: %s" % newqueuesize
            #     queuesize = newqueuesize
