from JumpScale import j
import JumpScale.baselib.redis
import time

descr = """
Monitor Redis status
"""

organization = "jumpscale"
name = 'redis_monitoring'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.redis"

period = 300 #always in sec
enable = True
async = False
roles = ["*"]


def action():
    import JumpScale.grid.gridhealthchecker
    redisclient = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

    nodeid = j.application.whoAmI.nid

    rstatus, errors = j.core.grid.healthchecker.checkRedis(nodeid)
    for data in [rstatus, errors]:
        if len(data) > 0:
            rstatus = rstatus[nodeid]['redis']
            for port, stat in rstatus.iteritems():
                if not stat['alive']:
                    redisclient.hset("healthcheck:status", 'redis:%s' % port, False)
                    msg='Redis on node with id %s with port %s is not running.' % (nodeid, port)
                    j.events.opserror( msg, category='monitoring')
                else:
                    redisclient.hset("healthcheck:status", 'redis:%s' % port, True)
                redisclient.hset("healthcheck:lastcheck", 'redis:%s' % port, time.time())