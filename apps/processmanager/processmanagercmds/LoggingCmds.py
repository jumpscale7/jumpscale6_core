from JumpScale import j
import ujson
import time


REDISIP = '127.0.0.1'
REDISPORT = 7768

class LoggingCmds(object):
    def __init__(self,daemon):
        self._name = "logging"
        self.daemon=daemon
        self.enabled = True
        self._adminAuth=daemon._adminAuth
        self.loghandlingpath = "/opt/jumpscale/apps/processmanager/loghandling/"
        self.ecohandlingpath = "/opt/jumpscale/apps/processmanager/eventhandling/"

        if not j.system.fs.exists(self.loghandlingpath) or not j.system.fs.exists(self.ecohandlingpath):
            self.enabled = False
            return

        self.logqueue = j.clients.redis.getGeventRedisQueue(REDISIP, REDISPORT, "logs")
        self.ecoqueue = j.clients.redis.getGeventRedisQueue(REDISIP, REDISPORT, "eco")

        client = j.core.osis.getClient(user='root')

        self.logclient = j.core.osis.getClientForCategory(client, "system", "log")
        self.ecoclient = j.core.osis.getClientForCategory(client, "system", "eco")

        self.log_te = j.core.taskletengine.get(self.loghandlingpath)
        self.eco_te = j.core.taskletengine.get(self.ecohandlingpath)

    def _init(self):
        if self.enabled:
            self.daemon.schedule("logging", self._handleLog)
            self.daemon.schedule("eco", self._handleEco)

    def _handleLog(self):
        out = list()
        lastsynced = time.time()
        while self.enabled:
            print 'FOUND LOG'
            log = ujson.decode(self.logqueue.get())
            log = j.logger.getLogObjectFromDict(log)
            log = self.log_te.executeV2(logobj=log)
            if log:
                out.append(log.__dict__)
            if len(out)>500 or lastsynced < time.time() - 5:
                self.logclient.set(out)
                out = list()
                lastsynced = time.time()

    def _handleEco(self):
        while self.enabled:
            print 'FOUND ECO'
            eco = ujson.decode(self.ecoqueue.get())
            eco["epoch"] = int(time.time())
            eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
            if not hasattr(eco, 'id'):
                eco.id = 0
            eco = self.eco_te.executeV2(eco=eco)
            if hasattr(eco,"tb"):
                delattr(eco, 'tb')
            self.ecoclient.set(eco.__dict__)
