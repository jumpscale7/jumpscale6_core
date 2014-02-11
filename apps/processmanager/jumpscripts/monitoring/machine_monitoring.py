from JumpScale import j

descr = """
gather statistics about machines
"""

organization = "jumpscale"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.machine"
period = 20 #always in sec
order = 1
enable=False
async=True

from xml.etree import ElementTree
try:
    import JumpScale.lib.qemu_img
except:
    enable=False

try:
    import libvirt
    con = libvirt.open('qemu:///system')
    #con = libvirt.open('qemu+ssh://10.101.190.24/system')
    stateMap = {libvirt.VIR_DOMAIN_RUNNING: 'RUNNING',
                libvirt.VIR_DOMAIN_NOSTATE: 'NOSTATE',
                libvirt.VIR_DOMAIN_PAUSED: 'PAUSED'}

except Exception, e:
    con = None

def action():
    if not con:
        return

    domains = con.listAllDomains()
    for domain in domains:
        machine = j.processmanager.cache.machineobject.get(id=domain.ID())
        machine.ckeyOld = machine.db.getContentKey()
        machine.db.name = domain.name()
        machine.db.nid = j.application.whoAmI.nid
        machine.db.gid = j.application.whoAmI.gid
        machine.db.mem = domain.memoryStats()['actual']
        machine.db.type = 'KVM'
        xml = ElementTree.fromstring(domain.XMLDesc())
        netaddr = dict()
        for interface in xml.findall('devices/interface'):
            mac = interface.find('mac').attrib['address']
            name = interface.find('alias').attrib['name']
            netaddr[mac] = [ name, None ]

        machine.db.netaddr = netaddr
        machine.db.lastcheck = machine.lastcheck
        machine.db.state = stateMap.get(domain.state()[0], 'STOPPED')
        machine.db.cpucore = int(xml.find('vcpu').text)

        if machine.ckeyOld != machine.db.getContentKey():
            #obj changed
            machine.send2osis()

        for disk in xml.findall('devices/disk'):
            if disk.attrib['device'] != 'disk':
                continue
            path = disk.find('source').attrib['dev']
            vdisk = j.processmanager.vdiskobject.get(id=path)
            vdisk.ckeyOld = vdisk.db.getContentKey()
            vdisk.db.path = path
            vdisk.db.type = disk.find('driver').attrib['type']
            vdisk.db.devicename = disk.find('target').attrib['dev']
            vdisk.db.machine_id = machine.db.id
            vdisk.db.active = j.system.fs.exists(path)
            if vdisk.db.active:
                diskinfo = j.system.platform.qemu_img.info(path)
                vdisk.db.size = diskinfo['virtual size']
                vdisk.db.sizeondisk = diskinfo['disk size']



            if vdisk.ckeyOld != vdisk.db.getContentKey():
                #obj changed
                vdisk.send2osis()

