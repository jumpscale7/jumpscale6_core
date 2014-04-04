

descr = """
send nic info to osis
"""

organization = "jumpscale"
author = "khamisr@incubaid.com"
license = "bsd"
version = "1.0"
category = "nic.send2osis"
period = 600 #always in sec
enable = True
async=True
queue='process'
roles = ["grid.node.network"]
from JumpScale import j

def action():
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()
    for cacheobj in j.core.processmanager.monObjects.nicobject.monitorobjects.itervalues():
        cacheobj.send2osis()
