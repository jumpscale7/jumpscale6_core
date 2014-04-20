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
log=False

def action():

    import JumpScale.baselib.redis

    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    timemap = {'default': '-2m', 'io': '-2h', 'hypervisor': '-10m'}
    prefix = 'workers__worker_'
    workers = [ x[len(prefix):] for x in j.tools.startupmanager.listProcesses() if x.startswith(prefix) ]
    workers2 = rediscl.hgetall("workers:watchdog")
    foundworkers={}
    for workername, timeout in zip(workers2[0::2], workers2[1::2]):
        foundworkers[workername]=timeout

    for worker in workers:
        timeout = timemap.get(worker.split('_')[0])
        lastactive=foundworkers.get('worker_%s' % worker, 0)
        if j.base.time.getEpochAgo(timeout) > lastactive:
            j.events.opserror('Worker %s seems to have timed out' % worker, 'monitoring')
