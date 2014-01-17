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

from xml.etree import ElementTree

try:
    import libvirt
    con = libvirt.open('qemu:///system')
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
