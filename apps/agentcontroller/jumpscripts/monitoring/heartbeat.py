from JumpScale import j

descr = """
heartbeat
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "system.heartbeat"
period = 1 #always in sec
order = 1
enable=True
async=False


def action():    
    # osis=j.core.osis.getClientForCategory(self.host.daemon.osis,"system","heartbeat")
    # obj={}
    # obj["nid"]=j.application.whoAmI.nid
    # obj["gid"]=j.application.whoAmI.gid
    # obj["lastcheck"]=j.base.time.getTimeEpoch()
    obj=j.core.processmanager.monObjects.heartbeatobject.osis.new()
    j.core.processmanager.monObjects.heartbeatobject.osis.set(obj.__dict__)

