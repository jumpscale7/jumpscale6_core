from JumpScale import j

descr = """
heartbeat
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.heartbeat"
period = 60 #always in sec
order = 1
enable = True
async = False


def action():
    obj = j.core.processmanager.monObjects.heartbeatobject.osis.new()
    j.core.processmanager.monObjects.heartbeatobject.osis.set(obj.__dict__)

