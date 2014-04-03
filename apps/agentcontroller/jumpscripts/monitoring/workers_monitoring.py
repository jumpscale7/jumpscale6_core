from JumpScale import j

descr = """
Monitor worker status
"""

organization = "jumpscale"
name = 'workers_monitoring'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.workers"

period = 10 #always in sec
enable = True
async = False
roles = ["*"]


def action():
    
    import JumpScale.baselib.redis
    import time


    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    workersCheck = {'worker_default_0': '-2m', 'worker_hypervisor_0': '-10m', 'worker_io_0': '-2h', 'worker_default_1': '-2m'}
    
    workers2 = rediscl.hgetall("workers:watchdog")
    foundworkers={}
    for workername, timeout in zip(workers2[0::2], workers2[1::2]):    
        foundworkers[workername]=timeout

    for worker, timeout in workersCheck.iteritems():
        lastactive=foundworkers[worker]
        if j.base.time.getEpochAgo(timeout) > lastactive:
            j.events.opserror('Worker %s seems to have timed out' % worker, 'monitoring')
            rediscl.hset("healthcheck:status", 'workers:%s' % worker, False)
            rediscl.hset("healthcheck:lastcheck", 'workers:%s' % worker, time.time())
        else:
            rediscl.hset("healthcheck:status", 'workers:%s' % worker, True)
            rediscl.hset("healthcheck:lastcheck", 'workers:%s' % worker, time.time())

    
