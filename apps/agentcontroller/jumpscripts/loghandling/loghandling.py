
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


import ujson
import JumpScale.baselib.redis
import time


REDISIP = '127.0.0.1'
REDISPORT = 7768

#WE HAVE THIS CODE TWICE, NO IDEA WHY
# class LoggingCmds():
#     def __init__(self):
#         self.loghandlingpath = "/opt/jumpscale/apps/processmanager/loghandling/"
#         self.ecohandlingpath = "/opt/jumpscale/apps/processmanager/eventhandling/"

#         if not j.system.fs.exists(self.loghandlingpath) or not j.system.fs.exists(self.ecohandlingpath):
#             self.enabled = False
#             return

#         self.logqueue = j.clients.redis.getGeventRedisQueue(REDISIP, REDISPORT, "logs")
#         self.ecoqueue = j.clients.redis.getGeventRedisQueue(REDISIP, REDISPORT, "eco")

#         client = j.core.osis.getClient(user='root')

#         self.logclient = j.core.osis.getClientForCategory(client, "system", "log")
#         self.ecoclient = j.core.osis.getClientForCategory(client, "system", "eco")

#         self.log_te = j.core.taskletengine.get(self.loghandlingpath)
#         self.eco_te = j.core.taskletengine.get(self.ecohandlingpath)

#     def handleLog(self):
#         out = list()
#         lastsynced = time.time()
#         while self.enabled:
#             log = ujson.decode(self.logqueue.get())
#             log = j.logger.getLogObjectFromDict(log)
#             log = self.log_te.executeV2(logobj=log)
#             if log:
#                 out.append(log.__dict__)
#             if len(out)>500 or lastsynced < time.time() - 5:
#                 self.logclient.set(out)
#                 out = list()
#                 lastsynced = time.time()

#     def handleEco(self):
#         while self.enabled:
#             eco = ujson.decode(self.ecoqueue.get())
#             eco["epoch"] = int(time.time())
#             eco = j.errorconditionhandler.getErrorConditionObject(ddict=eco)
#             if not hasattr(eco, 'id'):
#                 eco.id = 0
#             eco = self.eco_te.executeV2(eco=eco)
#             if hasattr(eco,"tb"):
#                 delattr(eco, 'tb')
#             self.ecoclient.set(eco.__dict__)



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
            eco.__dict__.pop("tb")        
        OSISclientEco.set(eco.__dict__)
        # eco=redisqueueEco.get_nowait()
