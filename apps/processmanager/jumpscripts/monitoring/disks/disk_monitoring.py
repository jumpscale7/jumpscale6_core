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
enable=False

def action():
    psutil=j.system.platform.psutil
    results={}
    nid = j.application.whoAmI.nid
    gid = j.application.whoAmI.gid

    disks=j.system.platform.diskmanager.partitionsFind(mounted=True)

    #disk counters

    counters=psutil.disk_io_counters(True)

    for disk in disks:
        disk.nid = nid
        disk.gid = gid
        disk.getSetGuid()
        path=disk.path.replace("/dev/","")
        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results["n%s.disk.%s.time.read"%(nid, path)]=read_time
            results["n%s.disk.%s.time.write"%(nid, path)]=write_time
            results["n%s.disk.%s.count.read"%(nid, path)]=read_count
            results["n%s.disk.%s.count.write"%(nid, path)]=write_count
            results["n%s.disk.%s.mbytes.read"%(nid, path)]=round(read_bytes/1024/1024,2)
            results["n%s.disk.%s.mbytes.write"%(nid, path)]=round(write_bytes/1024/1024,2)
            results["n%s.disk.%s.space.free"%(nid, path)]=disk.free
            results["n%s.disk.%s.space.used"%(nid, path)]=disk.size-disk.free
            results["n%s.disk.%s.space.percent"%(nid, path)]=round((float(disk.size-disk.free)/float(disk.size)),2)

    result2={}
    for key in results.keys():
        result2[key]=j.system.stataggregator.set(key,results[key],remember=True)



