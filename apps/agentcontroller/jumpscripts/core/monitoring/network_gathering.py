from JumpScale import j
import psutil

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.nic"
period = 300 #always in sec
enable=True
async=True
queue='process'
roles = []
log=False

def action():
    import statsd
    stats = statsd.StatsClient()
    pipe = stats.pipeline()
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()

    netinfo=j.system.net.getNetworkInfo()
    counters=psutil.network_io_counters(True)
    results = dict()
    for mac,val in netinfo.iteritems():

        name,ipaddr=val
        if ipaddr:
            ipaddr=ipaddr.split(",")
            if ipaddr==['']:
                ipaddr=[]
        else:
            ipaddr=[]


        nic_key=name
        result = dict()
        if counters.has_key(nic_key):
            cacheobj=j.core.processmanager.monObjects.nicobject.get(id=nic_key)
            results[nic_key] = cacheobj
            cacheobj.ckeyOld=cacheobj.db.getContentKey()

            counter=counters[nic_key]

            bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout=counter

            result['kbytes_sent'] = int(round(bytes_sent/1024.0,0))
            result['kbytes_recv'] = int(round(bytes_recv/1024.0,0))
            result['packets_sent'] = packets_sent
            result['packets_recv'] = packets_recv
            result['errin'] = errin
            result['errout'] = errout
            result['dropin'] = dropin
            result['dropout'] = dropout

            cacheobj.db.active=True
            cacheobj.db.ipaddr=ipaddr
            cacheobj.db.mac=mac
            cacheobj.db.name=name

            if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
                #obj changed
                cacheobj.send2osis()

            for key, value in result.iteritems():
                pipe.gauge("%s_%s_nic_%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid, name, key), value)
    pipe.send()

    #find deleted nices
    for nic_key in j.core.processmanager.monObjects.nicobject.monitorobjects.keys():

        #result is all found nicobject in this run (needs to be str otherwise child obj)
        if nic_key and not result.has_key(nic_key):
            if j.basetype.string.check(nic_key):
                #no longer active
                print "NO LONGER ACTIVE:%s"%cacheobj.db.name
                cacheobj=j.core.processmanager.monObjects.nicobject.get(nic_key) #is cached so low overhead
                cacheobj.active=False
                print "SEND NIC INFO TO OSIS"
                cacheobj.send2osis()

            #otherwise there is a memory leak
            j.core.processmanager.monObjects.nicobject.monitorobjects.pop(nic_key)

    j.core.processmanager.monObjects.nicobject.monitorobjects=result

if __name__ == '__main__':
    action()
