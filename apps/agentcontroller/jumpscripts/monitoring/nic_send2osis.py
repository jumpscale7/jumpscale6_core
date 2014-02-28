

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
async=False
roles = ["grid.node.network"]
from JumpScale import j

def action():
    for cacheobj in j.core.processmanager.monObjects.nicobject.monitorobjects.itervalues():
        cacheobj.send2osis()
