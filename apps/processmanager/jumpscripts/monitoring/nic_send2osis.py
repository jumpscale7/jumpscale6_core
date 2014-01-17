

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

from JumpScale import j

def action():
    for cacheobj in j.processmanager.cache.nicobject.monitorobjects.itervalues():
        cacheobj.send2osis()
