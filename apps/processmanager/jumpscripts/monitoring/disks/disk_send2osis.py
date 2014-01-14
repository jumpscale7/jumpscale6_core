

descr = """
gather statistics about disks
"""

organization = "jumpscale"
author = "khamisr@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.disk"
period = 300 #always in sec
enable = True

from JumpScale import j

def action():
    for disk in j.processmanager.disks:
        disk.gid = j.application.whoAmI.gid
        disk.nid = j.application.whoAmI.nid
        j.processmanager.cache.diskobject.set(disk.__dict__)
