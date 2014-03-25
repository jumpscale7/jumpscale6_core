from JumpScale import j
import JumpScale.baselib.redis
import time

descr = """
Monitor Redis and ProcessManager statuses
"""

organization = "jumpscale"
name = 'healthchecker_monitoring'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.healthchecker"

period = 1 #always in sec
enable = True
async = False
roles = ["*"]


def action():
    import JumpScale.grid.gridhealthchecker
    redisclient = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    healthy = {'processmanager':True, 'redis': True}
    nodeid = j.application.whoAmI.nid
    
    status = j.core.grid.healthchecker.checkProcessManagers(nodeid)
    if not status:
        healthy['processmanager'] = False
        j.errorconditionhandler.raiseOperationalWarning('ProcessManager on node with id %s is not running.' % nodeid, 'monitoring')

    rstatus = j.core.grid.healthchecker.checkRedis(nodeid)
    for port, stat in rstatus.iteritems():
        if not stat['alive']:
            healthy['redis'] = False
            j.errorconditionhandler.raiseOperationalWarning('Redis on node with id %s with port %s is not running.' % (nodeid, port), 'monitoring')

    for check in ['processmanager', 'redis']:
        redisclient.set("healthcheck:%s" % check, healthy[check])
    redisclient.set("healthcheck:time", time.time())