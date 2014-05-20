from JumpScale import j

descr = """
create and start a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
period = 0  # always in sec
enable = True
async = True
queue = 'hypervisor'

def action(networkid, publicip):
    DEFAULTGWIP = j.application.config.get("vfw.default.ip")
    BACKPLANE = 'vxbackend'
    import JumpScale.lib.routeros
    import libvirt
    import JumpScale.lib.ovsnetconfig
    nc = j.system.ovsnetconfig
    con = libvirt.open()

    import time
    data = {'nid': j.application.whoAmI.nid,
            'gid': j.application.whoAmI.gid
            }

    j.packages.findNewest('', 'routeros_config').install()

    networkidHex = '%04x' % int(networkid)
    networkname = "space_%s"  % networkidHex
    name = 'routeros_%s' % networkidHex
    destinationdir = '/mnt/vmstor/routeros/%s' % networkidHex



    def cleanup():
        print "CLEANUP: %s/%s"%(networkid,networkidHex)
        try:
            dom = con.lookupByName(name)
            dom.destroy()
            dom.undefine()
        except libvirt.libvirtError:
            pass
        j.system.fs.removeDirTree(destinationdir)
        def deleteNet(net):
            try:
                net.destroy()
            except:
                pass
            try:
                net.undefine()
            except:
                pass
        try:
            for net in con.listAllNetworks():
                if net.name() == networkname:
                    deleteNet(net)
                    break
        except:
            pass

    cleanup()

    #setup network vxlan
    nc.ensureVXNet(int(networkid), BACKPLANE)
    xml = '''  <network>
    <name>%(networkname)s</name>
    <forward mode="bridge"/>
    <bridge name='%(networkname)s'/>
     <virtualport type='openvswitch'/>
 </network>''' % {'networkname': networkname}
    private = con.networkDefineXML(xml)
    private.create()
    private.setAutostart(True)

    if j.system.net.tcpPortConnectionTest(DEFAULTGWIP,22,timeout=5):
        raise RuntimeError("Cannot continue, foudn VFW which is using the admin address & remove")
    j.system.fs.createDir(destinationdir)
    destinationfile = 'routeros-small-%s.qcow2' % networkidHex
    destinationfile = j.system.fs.joinPaths(destinationdir, destinationfile)
    imagedir = '/opt/jsbox/apps/routeros_template/routeros_template_backup'
    imagefile = j.system.fs.joinPaths(imagedir, 'routeros-small-NETWORK-ID.qcow2')
    xmlsource = j.system.fs.fileGetContents(j.system.fs.joinPaths(imagedir, 'routeros-template.xml'))
    xmlsource = xmlsource.replace('NETWORK-ID', networkidHex)
    j.system.fs.copyFile(imagefile, destinationfile)

    try:
        dom = con.defineXML(xmlsource)
        dom.create()
    except libvirt.libvirtError, e:
        cleanup()
        raise RuntimeError("Could not create VFW vm from template, network id:%s:%s\n%s"%(networkid,networkidHex,e))

    time.sleep(20)

    if j.system.net.tcpPortConnectionTest(DEFAULTGWIP,22,timeout=120):
        time.sleep(1)
    else:
        cleanup()
        raise RuntimeError("router did not become accessible over default internal net.")

    try:
        passwd=j.application.config.get("vfw.admin.passwd")
        ro=j.clients.routeros.get(DEFAULTGWIP,"vscalers",passwd)
        
        ro.do("/system/identity/set",{"name":"%s/%s"%(networkid,networkidHex)})
    except Exception,e:
        cleanup()
        raise RuntimeError("Could not connected to created VFW vm from template, network id:%s:%s\n%s"%(networkid,networkidHex,e)) 


    internalip = ro.networkId2NetworkAddr(networkid)
    data['internalip'] = internalip

    if not j.system.net.tcpPortConnectionTest(internalip,22,timeout=2):
        print "OK not other router found."
    else:
        cleanup()
        raise RuntimeError("IP conflict there is router with %s"%internalip)

    try:
        ro.ipaddr_set('internal', internalip+"/22", single=False)
    except Exception,e:
        cleanup()
        raise RuntimeError("Could not set internal ip on VFW, network id:%s:%s\n%s"%(networkid,networkidHex,e)) 

    time.sleep(2)
    print "wait max 30 sec on tcp port 22 connection to '%s'"%internalip
    if j.system.net.tcpPortConnectionTest(internalip,22,timeout=30):
        print "Router is accessible, initial configuration probably ok."
    else:
        cleanup()
        raise RuntimeError("Could not connect to router on %s"%internalip)

    ro=j.clients.routeros.get(internalip,"vscalers",passwd)

    try:
        ro.ipaddr_remove(DEFAULTGWIP)
        ro.resetMac("internal")
    except Exception,e:
        cleanup()
        raise RuntimeError("Could not cleanup VFW temp ip addr, network id:%s:%s\n%s"%(networkid,networkidHex,e)) 

    print "tcp port:22 test to 10.199.3.254, needs to be gone."
    if j.system.net.tcpPortConnectionTest(DEFAULTGWIP,22,timeout=1):
        cleanup()
        raise RuntimeError("Temp ip address still there, was not removed during install. network id:%s:%s\n%s"%(networkid,networkidHex,e)) 
    return data


