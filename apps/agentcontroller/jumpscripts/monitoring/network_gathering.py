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
period = 30 #always in sec
enable=True
async=False
roles = ["grid.node.network"]

#THINK NO LONGER REQUIRED
# if not hasattr(j, 'processmanager'):
#     enable = False
# else:
#     j.processmanager.nics = dict()

def action():

    def aggregate(cacheobj,nic_key,key,value,avg=True,ttype="N",percent=False):
        aggrkey="n%s.nic.%s.%s"%(j.application.whoAmI.nid,nic_key,key)
        j.system.stataggregator.set(aggrkey,value,ttype=ttype,remember=True,memonly=not(j.basetype.string.check(nic_key)),percent=percent)
        if avg:
            a,m=j.system.stataggregator.getAvgMax(aggrkey)
        else:
            a=value        
        cacheobj.db.__dict__[key]=a
        return cacheobj

    netinfo=j.system.net.getNetworkInfo()

    counters=psutil.network_io_counters(True)

    result={}
    for mac,val in netinfo.iteritems():

        name,ipaddr=val
        ipaddr=ipaddr.split(",")
        if ipaddr==['']:
            ipaddr=[]

        nic_key=name

        if counters.has_key(nic_key):
            
            cacheobj=j.core.processmanager.monObjects.nicobject.get(id=nic_key)

            cacheobj.ckeyOld=cacheobj.db.getContentKey()

            counter=counters[nic_key]

            bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout=counter

            cacheobj=aggregate(cacheobj,nic_key,"kbytes_sent",int(round(bytes_sent/1024,0)),avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"kbytes_recv",int(round(bytes_recv/1024,0)),avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"packets_sent",packets_sent,avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"packets_recv",packets_recv,avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"errin",errin,avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"errout",errout,avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"dropin",dropin,avg=True,ttype="D",percent=False)
            cacheobj=aggregate(cacheobj,nic_key,"dropout",dropout,avg=True,ttype="D",percent=False)        

            cacheobj.db.active=True
            cacheobj.db.ipaddr=ipaddr
            cacheobj.db.mac=mac
            cacheobj.db.name=name

            if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
                #obj changed
                cacheobj.send2osis()
                # print cacheobj.db

            result[nic_key]=cacheobj


    #find deleted nices
    for nic_key in j.core.processmanager.monObjects.nicobject.monitorobjects.keys():

        #result is all found nicobject in this run (needs to be str otherwise child obj)
        if nic_key and not result.has_key(nic_key):
                    
            if j.basetype.string.check(nic_key):
                #no longer active
                print "NO LONGER ACTIVE:%s"%cacheobj.db.name
                cacheobj=j.nicmanager.cache.nicobject.get(nic_key) #is cached so low overhead
                cacheobj.active=False
                cacheobj.send2osis()

            #otherwise there is a memory leak
            j.nicmanager.cache.nicobject.monitorobjects.pop(nic_key)
            #remove from aggregator
            aggrkey="n%s.nic.%s"%(j.application.whoAmI.nid,nic_key)
            j.system.stataggregator.delete(prefix=aggrkey)            

    j.core.processmanager.monObjects.nicobject.monitorobjects=result

