from JumpScale import j
import netaddr

class Netconfig:
    """
    """

    def __init__(self):
        self.root="/"

    def setRoot(self,root):
        self.root=root
        if not j.system.fs.exists(path=root):
            raise RuntimeError("Cannot find root for netconfig:%s"%root)
        #set base files
        for item in ["etc/network/interfaces","etc/resolv.conf"]:
            j.system.fs.touch(j.system.fs.joinPaths(self.root,item),overwrite=False)

    def shutdownNetwork(self,excludes=[]):
        """
        find all interfaces and shut them all down with ifdown
        this is to remove all networking things going on
        """
        excludes.append("lo")
        for nic in j.system.net.getNics():
            if nic not in excludes:
                cmd="ifdown %s --force"%nic
                print "shutdown:%s"%nic
                j.system.process.execute(cmd)

        
    def _getInterfacePath(self):
        path=j.system.fs.joinPaths(self.root,"etc/network/interfaces")
        if not j.system.fs.exists(path):
            raise RuntimeError("Could not find network interface path: %s"%path)
        return path

    def _backup(self,path):
        backuppath=path+".backup"
        counter=1
        while j.system.fs.exists(path=backuppath):
            counter+=1
            backuppath=path+".backup.%s"%counter
        j.system.fs.copyFile(path,backuppath)

    def reset(self,shutdown=False):
        """
        empty config of /etc/network/interfaces
        """
        if shutdown:
            self.shutdownNetwork()
        path=self._getInterfacePath()
        self._backup(path)
        j.system.fs.writeFile(path,"auto lo\n\n")
        

    def enableDhcpInterface(self,dev="eth0",start=False):

        C="""
auto $int
iface eth0 inet dhcp
"""
        C=C.replace("$int",dev)
        path=self._getInterfacePath()
        ed=j.codetools.getTextFileEditor(path)
        ed.setSection(dev,C)
        if start:
            cmd="ifup %s"%dev
            print "up:%s"%dev
            print cmd
            j.system.process.execute(cmd)     

    def remove(self,dev):
        path=self._getInterfacePath()
        ed=j.codetools.getTextFileEditor(path)
        ed.removeSection(dev)

    def setNameserver(self,addr):
        """
        resolvconf will be disabled
        
        """
        cmd="resolvconf --disable-updates"
        j.system.process.execute(cmd)
        C="nameserver %s\n"%addr    
        path=j.system.fs.joinPaths(self.root,"etc/resolv.conf")
        if not j.system.fs.exists(path):
            pass  #@todo???? does not work         
            # raise RuntimeError("Could not find resolv.conf path: '%s'"%path)
        j.system.fs.writeFile(path,C)


    def addIpaddrStatic(self,dev,ipaddr,gw=None,start=False):
        """
        ipaddr in form of 192.168.10.2/24 (can be list)
        gateway in form of 192.168.10.254
        """
        C="""
auto $int        
iface $int inet static
       address $ip
       netmask $mask
       network $net
"""
        args={}
        args["dev"]=dev
        args["ipaddr"]=ipaddr
        if gw<>None:
            args["gw"]=gw

        self._applyNetconfig(dev,C,args,start=start)

    def addIpaddrStaticBridge(self,dev,ipaddr,bridgedev,gw=None,start=False):
        """
        ipaddr in form of 192.168.10.2/24 (can be list)
        gateway in form of 192.168.10.254
        """
        C="""
auto $int        
iface $int inet static
       bridge_ports $bridgedev
       bridge_fd 0
       bridge_maxwait 0
       address $ip
       netmask $mask
       network $net
"""
        future="""
       #broadcast <broadcast IP here, e.g. 192.168.1.255>
       # dns-* options are implemented by the resolvconf package, if installed
       #dns-nameservers <name server IP address here, e.g. 192.168.1.1>
       #dns-search your.search.domain.here

"""
        args={}
        args["dev"]=dev
        args["ipaddr"]=ipaddr
        args["bridgedev"]=bridgedev        
        if gw<>None:
            args["gw"]=gw

        self._applyNetconfig(dev,C,args,start=start)        

    def _applyNetconfig(self,dev,template,args,start=False):
        C=template
        dev=args["dev"]
        ipaddr=args["ipaddr"]
        C=C.replace("$int",dev)
        ip = netaddr.IPNetwork(ipaddr)
        C=C.replace("$ip",str(ip.ip))
        C=C.replace("$mask",str(ip.netmask))
        C=C.replace("$net",str(ip.network))
        
        if args.has_key("gw"):
            C=C.replace("$gw","gateway %s"%args["gw"])
        if args.has_key("bridgedev"):
            C=C.replace("$bridgedev",args["bridgedev"])
        path=self._getInterfacePath()
        ed=j.codetools.getTextFileEditor(path)
        ed.setSection(dev,C)
        if start:
            cmd="ifup %s"%dev
            print "up:%s"%dev
            print cmd
            j.system.process.execute(cmd) 





