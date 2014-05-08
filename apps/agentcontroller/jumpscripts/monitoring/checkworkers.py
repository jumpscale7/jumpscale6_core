from JumpScale import j

descr = """
check if workers are running
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.checkworkers"
period = 10
enable=True
startatboot=False
async=False
log=False
roles = []



def action():
    import JumpScale.baselib.redis
    import time

    pds = j.tools.startupmanager.getProcessDefs('workers')
    nrworkersrequired = sum( [ pd.numprocesses for pd in pds ] )
    j.system.process.checkstart("jpackage start -n workers","worker.py --nodeid=%s" % j.application.whoAmI.nid,nrworkersrequired,retry=1)





