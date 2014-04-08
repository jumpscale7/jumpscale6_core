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
    timemap = {'default': '-2m', 'io': '-2h', 'hypervisor': '-10m'}
    result = dict()
    prefix = 'workers__worker_'
    workers = [ x[len(prefix):] for x in j.tools.startupmanager.listProcesses() if x.startswith(prefix) ]
    for worker in workers:
        timeout = timemap.get(worker.split('_')[0])
        lastactive = int(rediscl.hget('workers:watchdog', 'worker_%s' % worker))
        pids = j.system.process.getProcessPid(worker)
        stats = {'cpu': 0, 'mem': 0, 'lastactive': lastactive, 'state': 'HALTED'}
        for pid in pids:
            processobj = j.system.process.getProcessObject(pid)
            stats['cpu'] += processobj.get_cpu_percent()
            stats['mem'] += processobj.get_memory_info()[0]
        if j.base.time.getEpochAgo(timeout) < lastactive and pids:
            stats['state'] = 'RUNNING'
        result[worker] = stats
    return result
    
