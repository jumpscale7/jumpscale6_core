from JumpScale import j

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
    workers = ['worker_default_0', 'worker_hypervisor_0', 'worker_io_0', 'worker_default_1']
    result = dict()
    for worker in workers:
        pids = j.system.process.getProcessPid(worker)
        stats = {'cpu': 0, 'mem': 0}
        for pid in pids:
            processobj = j.system.process.getProcessObject(pid)
            stats['cpu'] += processobj.get_cpu_percent()
            stats['mem'] += processobj.get_memory_info()[0]
        result[worker] = stats
    return result
    
