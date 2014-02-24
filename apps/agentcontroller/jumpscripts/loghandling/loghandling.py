
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
async=True
log = False


import ujson
import JumpScale.baselib.redis
import time

REDISIP = '127.0.0.1'
REDISPORT = 7768

def action():

    redisqueue=j.clients.redis.getRedisQueue("127.0.0.1",7768,"logs")
    # redis=j.clients.redis.getRedisClient("127.0.0.1",7767)
    redisqueueEco=j.clients.redis.getRedisQueue("127.0.0.1",7768,"eco")

    OSISclient = j.core.osis.getClient(user='root')

    OSISclientLogger=j.core.osis.getClientForCategory(OSISclient,"system","log")
    OSISclientEco=j.core.osis.getClientForCategory(OSISclient,"system","eco")

    log = None
    path = "/opt/jumpscale/apps/processmanager/loghandling/"
    if j.system.fs.exists(path=path):
        loghandlingTE = j.core.taskletengine.get(path)
        log=redisqueue.get_nowait()
        # j.core.grid.logger.osis = OSISclientLogger
    else:
        loghandlingTE = None

    eco = None
    path = "/opt/jumpscale/apps/processmanager/eventhandling"
    if j.system.fs.exists(path=path):
        eventhandlingTE = j.core.taskletengine.get(path)
        eco=redisqueueEco.get_nowait()
    else:
        eventhandlingTE = None

    out=[]
    while log<>None:
        log2=ujson.decode(log)
        log3 = j.logger.getLogObjectFromDict(log2)
        log4= loghandlingTE.executeV2(logobj=log3)      
        if log4<>None:
            out.append(log4.__dict__)
        if len(out)>500:
            OSISclientLogger.set(out)
            out=[]
        log=redisqueue.get_nowait()
    if len(out)>0:
        OSISclientLogger.set(out)

    while eco<>None:
        eco2=ujson.decode(eco)
        eco2["epoch"] = int(time.time())
        eco3 = j.errorconditionhandler.getErrorConditionObject(ddict=eco2)        
        eco4= eventhandlingTE.executeV2(eco=eco3)
        if hasattr(eco4,"tb"):
            eco4.__dict__.pop("tb")        
        OSISclientEco.set(eco4.__dict__)
        eco=redisqueueEco.get_nowait()
