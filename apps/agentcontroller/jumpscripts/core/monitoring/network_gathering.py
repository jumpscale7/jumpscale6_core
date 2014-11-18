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
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()

    netinfo=j.system.net.getNetworkInfo()
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
        cacheobj=j.core.processmanager.monObjects.nicobject.get(id=nic_key)
        results[nic_key] = cacheobj
        cacheobj.ckeyOld=cacheobj.db.getContentKey()

        cacheobj.db.active=True
        cacheobj.db.ipaddr=ipaddr
        cacheobj.db.mac=mac
        cacheobj.db.name=name

        if cacheobj.ckeyOld<>cacheobj.db.getContentKey():
            #obj changed
            cacheobj.send2osis()

    ncl = j.core.osis.getClientForCategory(j.core.osis.client, "system", "nic")
    nics = ncl.search({'nid': j.application.whoAmI.nid, 'gid': j.application.whoAmI.gid})[1:]
    #find deleted nices
    for nic in nics:
        #result is all found nicobject in this run (needs to be str otherwise child obj)
        if nic['active'] and nic['name'] not in results:
            #no longer active
            print "NO LONGER ACTIVE:%s" % nic['name']
            nic['active'] = False
            ncl.set(nic)

if __name__ == '__main__':
    action()
