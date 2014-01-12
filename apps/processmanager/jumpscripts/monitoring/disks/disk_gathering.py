from JumpScale import j

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

j.processmanager.disks = dict()

def action():
    osis = j.processmanager.osis_disk
    disks = j.system.platform.diskmanager.partitionsFind(mounted=True)
    result = {}
    for disk in disks:
        if disk.id not in j.processmanager.disks:
            #NEW
            disk.gid = j.application.whoAmI.gid
            disk.nid = j.application.whoAmI.nid
            guid,new,changed = osis.set(disk)
            disk = osis.get(guid)
            result[disk.id] = disk

    for item in j.processmanager.disks.keys():
        if item not in result.keys():
            #DELETED
            osis.delete(j.processmanager.disks[item.id].guid)
            #@todo test P2            

    j.processmanager.disks = result
    


