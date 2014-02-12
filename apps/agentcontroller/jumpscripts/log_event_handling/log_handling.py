from JumpScale import j

descr = """
process logs queued in redis
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "log.handling.init"
period = 1 #always in sec
order = 1
enable=True
async=False
roles = ["grid.node"]

import ujson
import JumpScale.baselib.redis
import time


def action():

    redisqueue=j.clients.redis.getRedisQueue("127.0.0.1",7768,"logs")
    # redis=j.clients.redis.getRedisClient("127.0.0.1",7767)
    redisqueueEco=j.clients.redis.getRedisQueue("127.0.0.1",7768,"eco")

    OSISclient = j.core.osis.getClient(user='root')

    OSISclientLogger=j.core.osis.getClientForCategory(OSISclient,"system","log")
    OSISclientEco=j.core.osis.getClientForCategory(OSISclient,"system","eco")

    path = "/opt/jumpscale/apps/processmanager/loghandling/"
    if j.system.fs.exists(path=path):
        loghandlingTE = j.core.taskletengine.get(path)
        # j.core.grid.logger.osis = OSISclientLogger
    else:
        loghandlingTE = None

    path = "/opt/jumpscale/apps/processmanager/eventhandling"
    if j.system.fs.exists(path=path):
        eventhandlingTE = j.core.taskletengine.get(path)
        # j.core.grid.logger.osiseco = OSISclientEco
    else:
        eventhandlingTE = None

    log=redisqueue.get_nowait()
    out=[]
    while log<>None:
        log=ujson.decode(log)
        log = j.logger.getLogObjectFromDict(log)
        log= loghandlingTE.executeV2(logobj=log)
        if log<>None:
            out.append(log.__dict__)
        if len(out)>500:
            OSISclientLogger.set(out)
            out=[]
        log=redisqueue.get_nowait()
    if len(out)>0:
        OSISclientLogger.set(out)

    eco=redisqueueEco.get_nowait()
    while eco<>None:
        eco=ujson.decode(eco)
        eco["epoch"] = int(time.time())
        eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
        eco= eventhandlingTE.executeV2(eco=eco)
        if hasattr(eco,"tb"):
            delattr(eco, 'tb')
        OSISclientEco.set(eco.__dict__)
        eco=redisqueueEco.get_nowait()
