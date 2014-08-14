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
roles = []

log=False

def action():
    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', 7766)
    timemap = {'default': '-2m', 'io': '-2h', 'hypervisor': '-10m','process':'-1m'}
    result = dict()
    workers_processdefs = j.tools.startupmanager.getProcessDefs('workers')
    for processdef in workers_processdefs:
        for i in range(1, processdef.numprocesses + 1):
            worker = '%s_%s' % (processdef.name, i)
            lastactive = rediscl.hget('workers:watchdog', worker) or 0
            timeout = timemap.get(processdef.name.split('_')[1])
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
