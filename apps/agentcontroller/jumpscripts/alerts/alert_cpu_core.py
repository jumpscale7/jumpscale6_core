
from JumpScale import j

descr = """
Check on average cpu
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
period = 15*60  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False
queue ='process'
roles = ['master']


def action():
    import JumpScale.grid.osis
    ocl = j.core.osis.getClient(user='root')
    scl = j.core.osis.getClientForCategory(ocl, 'system', 'stats')
    results = scl.search({'target':'smartSummarize(n*.system.cpu.percent, "1hour", "avg")', 'from': '-1h'})
    for noderesult in results:
        avgcpu, timestamp = noderesult['datapoints'][-1]
        target = noderesult['target']
        if avgcpu > 80:
            nid = int(target[len('smartSummarize(n'):].split('.')[0])
            state = 'CRITICAL' if avgcpu > 95 else 'WARNING' 
            j.events.raiseAlert('cpu.core', state, avgcpu, nid=nid)
