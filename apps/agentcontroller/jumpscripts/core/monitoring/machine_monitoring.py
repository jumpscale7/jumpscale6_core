from JumpScale import j

descr = """
gather statistics about machines
"""

organization = "jumpscale"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
category = "monitoring.machine"
period = 60*2 #always in sec
order = 1
enable=True
async=True
queue='process'
log=False

roles = []

from xml.etree import ElementTree
try:
    import JumpScale.lib.qemu_img
    import libvirt
except:
    enable=False

def action():
    if not hasattr(j.core, 'processmanager'):
        import JumpScale.grid.processmanager
        j.core.processmanager.loadMonitorObjectTypes()

    con = libvirt.open('qemu:///system')
    #con = libvirt.open('qemu+ssh://10.101.190.24/system')
    stateMap = {libvirt.VIR_DOMAIN_RUNNING: 'RUNNING',
                libvirt.VIR_DOMAIN_NOSTATE: 'NOSTATE',
                libvirt.VIR_DOMAIN_PAUSED: 'PAUSED'}



    systemcl = j.core.osis.getClientForNamespace('system')
    allmachines = systemcl.machine.simpleSearch({})
    allmachines = { machine['id']: machine for machine in allmachines }
    domainmachines = list()
    try:
        domains = con.listAllDomains()
        for domain in domains:
            machine = j.core.processmanager.monObjects.machineobject.get(id=domain.ID())
            domainmachines.append(domain.ID())
            machine.ckeyOld = machine.db.getContentKey()
            machine.db.name = domain.name()
            machine.db.nid = j.application.whoAmI.nid
            machine.db.gid = j.application.whoAmI.gid
            machine.db.type = 'KVM'
            xml = ElementTree.fromstring(domain.XMLDesc())
            netaddr = dict()
            for interface in xml.findall('devices/interface'):
                mac = interface.find('mac').attrib['address']
                alias = interface.find('alias')
                name = None
                if alias is not None:
                    name = alias.attrib['name']
                netaddr[mac] = [ name, None ]

            machine.db.mem = int(xml.find('memory').text)

            machine.db.netaddr = netaddr
            machine.db.lastcheck = j.base.time.getTimeEpoch()
            machine.db.state = stateMap.get(domain.state()[0], 'STOPPED')
            machine.db.cpucore = int(xml.find('vcpu').text)


            # if machine.ckeyOld != machine.db.getContentKey():
            #     #obj changed
            try:
                machine.send2osis()
            except Exception:
                pass

            for disk in xml.findall('devices/disk'):
                if disk.attrib['device'] != 'disk':
                    continue
                diskattrib = disk.find('source').attrib
                path = diskattrib.get('dev', diskattrib.get('file'))
                vdisk = j.core.processmanager.monObjects.vdiskobject.get(id=path)
                vdisk.ckeyOld = vdisk.db.getContentKey()
                vdisk.db.path = path
                vdisk.db.type = disk.find('driver').attrib['type']
                vdisk.db.devicename = disk.find('target').attrib['dev']
                vdisk.db.machineid = machine.db.id
                vdisk.db.active = j.system.fs.exists(path)
                if vdisk.db.active:
                    try:
                        diskinfo = j.system.platform.qemu_img.info(path)
                        vdisk.db.size = diskinfo['virtual size']
                        vdisk.db.sizeondisk = diskinfo['disk size']
                        vdisk.db.backingpath = diskinfo.get('backing file', '')
                    except Exception:
                        # failed to get disk information
                        vdisk.db.size = -1
                        vdisk.db.sizeondisk = -1
                        vdisk.db.backingpath = ''

                if vdisk.ckeyOld != vdisk.db.getContentKey():
                    #obj changed
                    print "SEND VDISK INFO TO OSIS"
                    vdisk.send2osis()
    finally:
        deletedmachines = set(allmachines.keys()) - set(domainmachines)
        for deletedmachine in deletedmachines:
            machine = allmachines[deletedmachine]
            machine['state'] = 'DELETED'
            try:
                machine.send2osis()
            except Exception:
                pass
        con.close()

