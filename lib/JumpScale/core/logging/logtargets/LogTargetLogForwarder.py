# import socket
from JumpScale import j
from gevent import Greenlet
import gevent
import time
import Queue


TIMEOUT = 5
QUEUESIZE = 1000


class DropQueue(Queue.Queue):
    def put(self, item, block=True, timeout=None):
        if self.qsize() == self.maxsize:
            # queue is full dropping one
            try:
                self.get(False)
            except Queue.Empty:
                pass
        return Queue.Queue.put(self, item, block, timeout)

class LogScheduler(Greenlet):
    def __init__(self, handler, *args, **kwargs):
        super(LogScheduler, self).__init__(*args, **kwargs)
        self._handler = handler

    def _run(self, *args, **kwargs):
        while True:
            gevent.sleep(5)
            records = list()
            for _ in xrange(self._handler._logqueue.qsize()):
                records.append(self._handler._logqueue.get())
            if records:
                self._handler.logBatch(records)

class LogTargetLogForwarder():
    """Forwards incoming logRecords to localclientdaemon"""
    def __init__(self, serverip=None, bulk=False):
        self.bulk = True
        self._lastcheck = 0
        self._logqueue = DropQueue(QUEUESIZE)
        self._ecoqueue = DropQueue(QUEUESIZE)
        self._batchqueue = DropQueue(QUEUESIZE)
        self.connected = False

        if j.application.appname=="osisserver":
            self.enabled = False
        else:
            #do not put on on, too dangerous, to many apps cannot & should not use it, only when in grid mode we should
            self.enabled = True

        if not serverip:
            if j.application.config.exists('grid.master.ip'):
                serverip = j.application.config.get("grid.master.ip")
                if serverip=="":
                    raise RuntimeError("grid.master.ip found but not filled in")
            if not serverip:
                self.enabled = False
                return
        self.serverip = serverip
        self.loggerClient=None
        self.checkTarget()
        if self.bulk:
            LogScheduler(self).start()

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if self._lastcheck + TIMEOUT > time.time():
            return self.connected
        self.connected = j.system.net.tcpPortConnectionTest(self.serverip,4443)
        self._lastcheck = time.time()
        if not self.connected:
            print "Could not connect to logforwarder will try again in 5 seconds."
            return self.connected

        import JumpScale.grid
        if self.loggerClient==None:
            self.loggerClient=j.core.grid.getZLoggerClient(ipaddr=self.serverip)
            j.logger.logTargetLogForwarder=self
        if not self.bulk:
            self._processQueue(self._logqueue, self.log)
        self._processQueue(self._ecoqueue, self.logECO)
        self._processQueue(self._batchqueue, self.logBatch)
        return self.connected

    def _processQueue(self, queue, method):
        while True:
            try:
                msg = queue.get(False)
            except Queue.Empty:
                break
            method(msg)

    def __str__(self):
        """ string representation of a LogTargetServer to ES"""
        return 'LogTargetLogServer logging to %s' % (str(self.serverip))

    __repr__ = __str__

    def logECO(self, eco):
        if self.enabled:
            if not self.checkTarget():
                self._ecoqueue.put(eco)
                return
            try:
                self.loggerClient.logECO(eco)
            except:
                print 'Failed to log in %s' % self
                self.connected = False

    def log(self, log):
        """
        forward the already encoded message to the target destination
        """
        if self.enabled:
            if not self.checkTarget() or self.bulk:
                self._logqueue.put(log)
                return

            try:
                self.loggerClient.log(log)
            except Exception,e:                
                print 'Failed to log in %s,error:%s' % (self,e)
                self.connected = False


    def logBatch(self, batch):
        """
        forward the already encoded message to the target destination
        """
        if self.enabled:
            if not self.checkTarget():
                self._batchqueue.put(batch)
                return

            try:
                self.loggerClient.logbatch(batch)
            except Exception,e:                
                print 'Failed to log in %s,error:%s' % (self,e)
                self.connected = False

