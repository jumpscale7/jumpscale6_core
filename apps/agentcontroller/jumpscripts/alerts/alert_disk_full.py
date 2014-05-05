
from JumpScale import j

descr = """
Check on disk fullness
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
period = 60  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False
queue ='process'
roles = ['master']


def action():
    import JumpScale.grid.osis
    import JumpScale.baselib.watchdog.client
    ocl = j.core.osis.getClient(user='root')
    scl = j.core.osis.getClientForCategory(ocl, 'system', 'stats')
    results = scl.search({'target':'smartSummarize(n*.disk.*.space_percent, "15min", "avg")', 'from': '-15min'})
    for noderesult in results:
        diskusage, timestamp = noderesult['datapoints'][-1]
        target = noderesult['target']

        nid = int(target[len('smartSummarize(n'):].split('.')[0])
        state = 'CRITICAL' if diskusage > 95 else 'WARNING' #95 still to be spec'ed.
        j.tools.watchdog.client.send('disk.full', state, diskusage, nid=nid)
