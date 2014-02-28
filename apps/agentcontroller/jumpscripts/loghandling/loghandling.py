
from JumpScale import j

descr = """
process logs queued in redis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "log.handling.init"
period = 1  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False


import ujson
import time
import JumpScale.baselib.redis

REDISIP = '127.0.0.1'
REDISPORT = 7768


def action():
    import gevent

    redisqueue = j.clients.redis.getGeventRedisQueue("127.0.0.1", 7768, "logs")
    redisqueueEco = j.clients.redis.getGeventRedisQueue("127.0.0.1", 7768, "eco")

    masterip = j.application.config.get('grid.master.ip')
    masterport = j.application.config.get('grid.master.port')

    OSISclient = j.core.osis.getClient(ipaddr=masterip, port=masterport, user='root')

    OSISclientLogger = j.core.osis.getClientForCategory(OSISclient, "system", "log")
    OSISclientEco = j.core.osis.getClientForCategory(OSISclient, "system", "eco")

    path = "/opt/jumpscale/apps/processmanager/loghandling/"
    if j.system.fs.exists(path=path):
        loghandlingTE = j.core.taskletengine.get(path)
    else:
        loghandlingTE = None

    path = "/opt/jumpscale/apps/processmanager/eventhandling"
    if j.system.fs.exists(path=path):
        eventhandlingTE = j.core.taskletengine.get(path)
    else:
        eventhandlingTE = None

    def processLogs():
        while True:
            out = list()
            log = redisqueue.get()
            for _ in xrange(redisqueue.qsize() + 1):
                if not log:
                    log = redisqueue.get()
                log = ujson.decode(log)
                log = j.logger.getLogObjectFromDict(log)
                log = loghandlingTE.executeV2(logobj=log)
                out.append(log.__dict__)
                log = None
            OSISclientLogger.set(out)

    def processECO():
        while True:
            eco = redisqueueEco.get()
            eco2 = ujson.decode(eco)
            eco2["epoch"] = int(time.time())
            eco3 = j.errorconditionhandler.getErrorConditionObject(ddict=eco2)
            eco4 = eventhandlingTE.executeV2(eco=eco3)
            if hasattr(eco4, "tb"):
                eco4.__dict__.pop("tb")
            OSISclientEco.set(eco4.__dict__)

    if loghandlingTE:
        gevent.Greenlet(processLogs).start()
    if eventhandlingTE:
        gevent.Greenlet(processECO).start()
