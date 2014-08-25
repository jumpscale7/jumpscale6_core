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

    disks = j.system.platform.diskmanager.partitionsFind(mounted=True, prefix='', minsize=0, maxsize=None)

    #disk counters
    counters=psutil.disk_io_counters(True)

    for disk in disks:
        results = dict()
        path=disk.path.replace("/dev/","")

        disk_key=path
        results['disk_id'] = disk_key
        cacheobj=j.core.processmanager.monObjects.diskobject.get(id=disk_key)
        cacheobj.ckeyOld=cacheobj.db.getContentKey()
        disk.nid = j.application.whoAmI.nid

        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results['time_read'] = cacheobj.db.__dict__['time_read'] = read_time
            results['time_write'] = cacheobj.db.__dict__['time_write'] = write_time
            results['count_read'] = cacheobj.db.__dict__['count_read'] = read_count
            results['count_write'] = cacheobj.db.__dict__['count_write'] = write_count

            read_bytes=int(round(read_bytes/1024,0))
            write_bytes=int(round(write_bytes/1024,0))
            results['kbytes_read'] = cacheobj.db.__dict__['kbytes_read'] = read_bytes
            results['kbytes_write'] = cacheobj.db.__dict__['kbytes_write'] = write_bytes
            results['space_free_mb'] = cacheobj.db.__dict__['space_free_mb'] = disk.free
            results['space_used_mb'] = cacheobj.db.__dict__['space_used_mb'] = disk.size-disk.free
            results['space_percent'] = cacheobj.db.__dict__['space_percent'] = round((float(disk.size-disk.free)/float(disk.size)),2)

        if (disk.free and disk.size) and (disk.free / float(disk.size)) * 100 < 10:
            j.events.opserror('Disk %s has less then 10%% free space' % disk.path, 'monitoring')

        for key,value in disk.__dict__.iteritems():
            cacheobj.db.__dict__[key]=value

        if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
            #obj changed
            print "SEND DISK INFO TO OSIS"
            cacheobj.send2osis()

        j.system.redisstataggregator.pushStats('disk', results)
