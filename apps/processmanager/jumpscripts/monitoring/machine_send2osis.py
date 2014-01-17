

descr = """
send machine info to osis
"""

organization = "jumpscale"
author = "khamisr@incubaid.com"
license = "bsd"
version = "1.0"
category = "machine.send2osis"
period = 3600 #always in sec
enable = True

from JumpScale import j

def action():
    for cacheobj in j.processmanager.cache.machineobject.monitorobjects.itervalues():
        cacheobj.send2osis()
