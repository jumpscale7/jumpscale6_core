from JumpScale import j
import JumpScale.baselib.redis

descr = """
Monitor CPU and mem of worker
"""

organization = "jumpscale"
name = 'workerstatus'
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "system.workerstatus"

async = False
roles = ["*"]


def action():
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)
    workers = {'worker_default_0': '-2m', 'worker_hypervisor_0': '-10m', 'worker_io_0': '-2h', 'worker_default_1': '-2m'}
    result = dict()
    for worker, timeout in workers.iteritems():
        lastactive = rediscl.hget('workers:watchdog', worker)
        pids = j.system.process.getProcessPid(worker)
        stats = {'cpu': 0, 'mem': 0, 'lastactive': lastactive, 'status': False}
        for pid in pids:
            processobj = j.system.process.getProcessObject(pid)
            stats['cpu'] += processobj.get_cpu_percent()
            stats['mem'] += processobj.get_memory_info()[0]
        if j.base.time.getEpochAgo(timeout) < lastactive:
            stats['status'] = True
        result[worker] = stats
    return result
    
