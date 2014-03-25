from JumpScale import j
import JumpScale.baselib.redis

descr = """
Monitor CPU and mem of worker
"""

organization = "jumpscale"
name = 'workerswatchdog'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "monitor.workerswatchdog"

period = 900 #always in sec
enable = True
async = False
roles = ["*"]


def action():
    healthy = True
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    workers = {'worker_default_0': '-2m', 'worker_hypervisor_0': '-10m', 'worker_io_0': '-2h', 'worker_default_1': '-2m'}
    for worker, timeout in workers.iteritems():
        lastactive = int(rediscl.hget('workers:watchdog', worker))
        if j.base.time.getEpochAgo(timeout) > lastactive:
            j.errorconditionhandler.raiseOperationalWarning('Worker %s seems to have timed out' % worker, 'monitoring')
            healthy = False
    
    rediscl.set("healthcheck:workers", healthy)
    
