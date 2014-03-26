from JumpScale import j
import JumpScale.baselib.redis
import time

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
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    workers = {'worker_default_0': '-2m', 'worker_hypervisor_0': '-10m', 'worker_io_0': '-2h', 'worker_default_1': '-2m'}
    for worker, timeout in workers.iteritems():
        lastactive = int(rediscl.hget('workers:watchdog', worker))
        if j.base.time.getEpochAgo(timeout) > lastactive:
            j.events.opserror_critical('Worker %s seems to have timed out' % worker, 'monitoring')
            
            rediscl.hset("healthcheck:status", 'workers:%s' % worker, True)
            rediscl.hset("healthcheck:lastcheck", 'workers:%s' % worker, time.time())
        else:
            rediscl.hset("healthcheck:status", 'workers:%s' % worker, True)
            rediscl.hset("healthcheck:lastcheck", 'workers:%s' % worker, time.time())
    
