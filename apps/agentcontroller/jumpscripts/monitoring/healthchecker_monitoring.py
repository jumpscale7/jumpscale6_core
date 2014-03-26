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

period = 600 #always in sec
enable = False
async = False
roles = ["*"]


def action():
    import JumpScale.grid.gridhealthchecker
    redisclient = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    healthy = {'processmanager':True, 'redis': True}
    nodeid = j.application.whoAmI.nid
    
    status = j.core.grid.healthchecker.checkProcessManager(nodeid)  #execute heartbeat on each node and see if result came in osis
    if not status:
        healthy['processmanager'] = False
        msg='ProcessManager on node with id %s is not running.' % nodeid
        j.events.opserror_critical( msg, category='monitoring')

    rstatus = j.core.grid.healthchecker.checkRedis(nodeid)
    for port, stat in rstatus.iteritems():
        if not stat['alive']:
            healthy['redis'] = False
            msg='Redis on node with id %s with port %s is not running.' % (nodeid, port)
            j.events.opserror_critical( msg, category='monitoring')

    for check in ['processmanager', 'redis']:
        redisclient.set("healthcheck:%s" % check, healthy[check])
    redisclient.set("healthcheck:time", time.time())