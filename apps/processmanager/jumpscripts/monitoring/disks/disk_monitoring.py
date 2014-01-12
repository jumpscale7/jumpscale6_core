from JumpScale import j

descr = """
gather statistics about disks
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.disk"
period = 20 #always in sec
order = 1
enable=True

def action():
    psutil=j.system.platform.psutil
    results={}
    nid = j.application.whoAmI.nid

    disks=j.system.platform.diskmanager.partitionsFind(mounted=True)

    #disk counters

    counters=psutil.disk_io_counters(True)

    for disk in disks:
        path=disk.path.replace("/dev/","")
        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results["n%s.d%s.time.read"%(nid, disk.id)]=read_time
            results["n%s.d%s.time.write"%(nid, disk.id)]=write_time
            results["n%s.d%s.count.read"%(nid, disk.id)]=read_count
            results["n%s.d%s.count.write"%(nid, disk.id)]=write_count
            results["n%s.d%s.mbytes.read"%(nid, disk.id)]=round(read_bytes/1024/1024,2)
            results["n%s.d%s.mbytes.write"%(nid, disk.id)]=round(write_bytes/1024/1024,2)
            results["n%s.d%s.space.free"%(nid, disk.id)]=disk.free
            results["n%s.d%s.space.used"%(nid, disk.id)]=disk.size-disk.free
            results["n%s.d%s.space.percent"%(nid, disk.id)]=round((float(disk.size-disk.free)/float(disk.size)),2)

    result2={}
    for key in results.keys():
        result2[key]=j.system.stataggregator.set(key,results[key],remember=True)



