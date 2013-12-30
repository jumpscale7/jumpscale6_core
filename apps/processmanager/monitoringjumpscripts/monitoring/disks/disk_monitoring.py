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

    disks=j.system.platform.diskmanager.partitionsFind(mounted=True)

    #disk counters

    counters=psutil.disk_io_counters(True)

    for disk in disks:
        path=disk.path.replace("/dev/","")
        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results["d%s.time.read"%(disk.id)]=read_time
            results["d%s.time.write"%(disk.id)]=write_time
            results["d%s.count.read"%(disk.id)]=read_count
            results["d%s.count.write"%(disk.id)]=write_count
            results["d%s.mbytes.read"%(disk.id)]=round(read_bytes/1024/1024,2)
            results["d%s.mbytes.write"%(disk.id)]=round(write_bytes/1024/1024,2)
            results["d%s.space.free"%(disk.id)]=disk.free
            results["d%s.space.used"%(disk.id)]=disk.size-disk.free
            results["d%s.space.percent"%(disk.id)]=round((float(disk.size-disk.free)/float(disk.size)),2)

    result2={}
    for key in results.keys():
        result2[key]=j.system.stataggregator.set(key,results[key],remember=True)



