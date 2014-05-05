
from JumpScale import j

descr = """
Check on grid health
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
period = 60*15  # always in sec
startatboot = True
order = 1
enable = True
async = True
log = False
queue ='process'
roles = ['master']


def action():
    import JumpScale.grid.gridhealthchecker
    import JumpScale.baselib.watchdog.client
    results, errors = j.core.grid.healthchecker.runAll()
    for nid, error in errors:
        j.tools.watchdog.client.send("grid.healthcheck","CRITICAL", -1, nid=nid)
