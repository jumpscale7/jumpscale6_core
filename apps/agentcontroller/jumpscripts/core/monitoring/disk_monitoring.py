from JumpScale import j
import time

descr = """
gather statistics about disks
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "disk.monitoring"
period = 300 #always in sec
order = 1
enable=True
async=True
queue='process'
log=False

roles = []

def action():
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()

    psutil=j.system.platform.psutil

    # def aggregate(cacheobj,disk_key,key,value,avg=True,ttype="N",percent=False):
    #     aggrkey="n%s.disk.%s.%s"%(j.application.whoAmI.nid,disk_key,key)
    #     j.system.stataggregator.set(aggrkey,value,ttype=ttype,remember=True,memonly=not(j.basetype.string.check(disk_key)),percent=percent)
        # if avg:
        #     a,m=j.system.stataggregator.getAvgMax(aggrkey)
        # else:
        #     a=value        
        # cacheobj.db.__dict__[key]=a
        # return cacheobj

    disks = j.system.platform.diskmanager.partitionsFind(mounted=True, prefix='', minsize=0, maxsize=None)

    #disk counters
    counters=psutil.disk_io_counters(True)

    for disk in disks:
        results = dict()
        path=disk.path.replace("/dev/","")

        disk_key=path
        results['disk_id'] = disk_key
        # cacheobj=j.core.processmanager.monObjects.diskobject.get(id=disk_key)

        # cacheobj.ckeyOld=cacheobj.db.getContentKey()
        # disk.nid = j.application.whoAmI.nid

        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results['time_read'] = read_time
            results['time_write'] = write_time
            results['count_read'] = read_count
            results['count_write'] = write_count
            # cacheobj=aggregate(cacheobj,disk_key,"time_read",read_time,avg=True,ttype="D",percent=True)
            # cacheobj=aggregate(cacheobj,disk_key,"time_write",write_time,avg=True,ttype="D",percent=True)
            # cacheobj=aggregate(cacheobj,disk_key,"count_read",read_count,avg=True,ttype="D",percent=False)
            # cacheobj=aggregate(cacheobj,disk_key,"count_write",write_count,avg=True,ttype="D",percent=False)

            read_bytes=int(round(read_bytes/1024,0))
            write_bytes=int(round(write_bytes/1024,0))
            results['kbytes_read'] = read_bytes
            results['kbytes_write'] = write_bytes
            # cacheobj=aggregate(cacheobj,disk_key,"kbytes_read",read_bytes,avg=True,ttype="D",percent=False)
            # cacheobj=aggregate(cacheobj,disk_key,"kbytes_write",write_bytes,avg=True,ttype="D",percent=False)
            results['space_free_mb'] = disk.free
            results['space_used_mb'] = disk.size-disk.free
            results['space_percent'] = round((float(disk.size-disk.free)/float(disk.size)),2)
            # cacheobj=aggregate(cacheobj,disk_key,"space_free_mb",disk.free,avg=True,ttype="N",percent=False)
            # cacheobj=aggregate(cacheobj,disk_key,"space_used_mb",disk.size-disk.free,avg=True,ttype="N",percent=False)
            # cacheobj=aggregate(cacheobj,disk_key,"space_percent",round((float(disk.size-disk.free)/float(disk.size)),2),avg=True,ttype="N",percent=True)

        if (disk.free and disk.size) and (disk.free / float(disk.size)) * 100 < 10:
            j.events.opserror('Disk %s has less then 10%% free space' % disk.path, 'monitoring')

        for key,value in disk.__dict__.iteritems():
            cacheobj.db.__dict__[key]=value

        # if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
        #     #obj changed
        #     print "SEND DISK INFO TO OSIS"
        #     cacheobj.send2osis()

        j.system.redisstataggregator.pushStats('disk', results)
