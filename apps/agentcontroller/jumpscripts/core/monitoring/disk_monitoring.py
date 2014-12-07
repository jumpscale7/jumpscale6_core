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
    import JumpScale.lib.diskmanager
    import statsd
    stats = statsd.StatsClient()
    pipe = stats.pipeline()
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()

    psutil=j.system.platform.psutil

    disks = j.system.platform.diskmanager.partitionsFind(mounted=True, prefix='', minsize=0, maxsize=None)

    #disk counters
    counters=psutil.disk_io_counters(True)

    for disk in disks:
        results = {'time_read': 0, 'time_write': 0, 'count_read': 0, 'count_write': 0,
                   'kbytes_read': 0, 'kbytes_write': 0, 
                   'space_free_mb': 0, 'space_used_mb': 0, 'space_percent': 0}
        path=disk.path.replace("/dev/","")

        disk_key=path
        cacheobj=j.core.processmanager.monObjects.diskobject.get(id=disk_key)
        cacheobj.ckeyOld=cacheobj.db.getContentKey()
        disk.nid = j.application.whoAmI.nid

        if counters.has_key(path):
            counter=counters[path]
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results['time_read'] = read_time
            results['time_write'] = write_time
            results['count_read'] = read_count
            results['count_write'] = write_count

            read_bytes=int(round(read_bytes/1024,0))
            write_bytes=int(round(write_bytes/1024,0))
            results['kbytes_read'] = read_bytes
            results['kbytes_write'] = write_bytes
            results['space_free_mb'] = int(round(disk.free))
            results['space_used_mb'] = int(round(disk.size-disk.free))
            results['space_percent'] = int(round((float(disk.size-disk.free)/float(disk.size)),2))

        for key,value in disk.__dict__.iteritems():
            cacheobj.db.__dict__[key]=value

        if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
            #obj changed
            print "SEND DISK INFO TO OSIS"
            cacheobj.send2osis()

        for key, value in results.iteritems():
            pipe.gauge("%s_%s_disk_%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid, path, key), value)

    pipe.send()


if __name__ == '__main__':
    action()
