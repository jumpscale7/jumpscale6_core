from JumpScale import j
import JumpScale.grid.osis

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
    osiscl = j.core.osis.getClient(user='root')
    hbcl = j.core.osis.getClientForCategory(osiscl, 'system', 'heartbeat')
    obj = hbcl.new()
    hbcl.set(obj)

    #heartbeat for processmanager

