from JumpScale import j

descr = """
gather statistics about system
"""

organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
category = "info.gather.nic"
period = 300 #always in sec
enable=False

j.processmanager.nics = dict()

def action():
    osis=j.processmanager.osis_nic
    netinfo=j.system.net.getNetworkInfo()
    result={}
    for mac,val in netinfo.iteritems():
        name,ipaddr=val
        ipaddr=ipaddr.split(",")
        if ipaddr==['']:
            ipaddr=[]

        if not j.processmanager.nics.has_key(name):
            #NEW
            nic=osis.new()
            nic.active=True
            nic.ipaddr=ipaddr
            nic.mac=mac
            nic.name=name
            nic.gid=j.application.whoAmI.gid
            nic.nid=j.application.whoAmI.nid

            guid,new,changed=osis.set(nic)
            nic=osis.get(guid)
            result[name]=nic

    for item in j.processmanager.nics.keys():
        if item not in result:
            osis.delete(j.processmanager.nics[item].guid)

    j.processmanager.nics=result

