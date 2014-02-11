# import socket
from JumpScale import j
import time
import ujson
import JumpScale.baselib.redis

TIMEOUT = 5

class LogTargetLogForwarder():
    """Forwards incoming logRecords to redis"""

    def __init__(self, serverip="127.0.0.1",port=7767):

        self.serverip=serverip
        self.port=port

        self._lastcheck = 0
        self.connected = False

        if j.application.appname=="osisserver":
            self.enabled = False
        else:
            #do not put on on, too dangerous, to many apps cannot & should not use it, only when in grid mode we should
            self.enabled = True

        self.redisqueue=None

        self.checkTarget()

    def checkTarget(self):
        """
        check status of target, if ok return True
        """
        if self._lastcheck + TIMEOUT > time.time():
            return self.connected

        #redis & processmanager need to be active
        self.connected = j.system.net.tcpPortConnectionTest(self.serverip,7767) and j.system.net.tcpPortConnectionTest(self.serverip,4445)

        self._lastcheck = time.time()
        if not self.connected:
            print "Could not connect to redis will try again in 5 seconds."
            return self.connected

        self.redisqueue=j.clients.redis.getRedisQueue(self.serverip,self.port,"logs")
        self.redisqueueEco=j.clients.redis.getRedisQueue(self.serverip,self.port,"eco")

        return self.connected


    def __str__(self):
        return 'LogTargetToRedis logging to %s' % (str(self.serverip))

    __repr__ = __str__

    def logECO(self, eco):
        if self.enabled:
            eco = eco.__dict__.copy()
            eco.pop('tb', None)
            eco = j.errorconditionhandler.getErrorConditionObject(eco)
            if self.checkTarget():
                try:
                    self.redisqueueEco.put(ujson.dumps(eco.__dict__))
                except Exception, e:
                    print 'Failed to log in %s error: %s' % (self, e)
                    self.connected = False

    def log(self, log):
        """
        forward the already encoded message to the target destination
        """
        if self.enabled:
            if self.checkTarget():
                try:
                    self.redisqueue.put(ujson.dumps(log.__dict__))
                except Exception,e:                
                    print 'Failed to log in %s,error:%s' % (self,e)
                    self.connected = False

