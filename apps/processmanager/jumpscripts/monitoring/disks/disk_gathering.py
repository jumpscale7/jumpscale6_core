

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
j.processmanager.disks = dict()

def action(j):
    
    osis = j.processmanager.osis_disk
    disks = j.system.platform.diskmanager.partitionsFind(mounted=True)
    result = {}
    for disk in disks:
        if not j.processmanager.disks.has_key(disk.id):
            #NEW
            disk.gid = j.application.whoAmI.gid
            disk.nid = j.application.whoAmI.nid
            guid,new,changed = osis.set(disk.__dict__)
            disk = osis.get(guid)
            result[disk.id] = disk
        else:
            disk=result[disk.id]



    for item in j.processmanager.disks.keys():
        if item not in result.keys():
            #DELETED
            osis.delete(j.processmanager.disks[item.id].guid)
            #@todo test P2            

    j.processmanager.disks = result
    


