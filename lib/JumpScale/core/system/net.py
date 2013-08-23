

import time
import socket
import re

from OpenWizzy import o

class SystemNet:

    def __init__(self):
        self._windowsNetworkInfo = None

    def tcpPortConnectionTest(self,ipaddr,port):
        conn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((ipaddr,port))
        except:
            return False
        return True
        
    def waitConnectionTest(self,ipaddr,port,timeout):
        """
        will return false if not successfull (timeout)
        """
        o.logger.log("test tcp connection to '%s' on port %s"%(ipaddr,port))
        if ipaddr.strip()=="localhost":
            ipaddr="127.0.0.1"
        port=int(port)
        start=o.base.time.getTimeEpoch()
        now=start
        while now<start+timeout:
            if o.system.net.tcpPortConnectionTest(ipaddr,port):
                return True
            now=o.base.time.getTimeEpoch()
        return False


    def checkListenPort(self, port):
        """
        Check if a certain port is listening on the system.

        @param port: sets the port number to check
        @return status: 0 if running 1 if not running
        """
        if port >65535 or port <0 :
            raise ValueError("Port cannot be bigger then 65535 or lower then 0")

        o.logger.log('Checking whether a service is running on port %d' % port, 8)

        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            # netstat: n == numeric, -t == tcp, -u = udp, l= only listening, p = program
            command = "netstat -ntulp | grep ':%s '" % port
            (exitcode, output) = o.system.process.execute(command, dieOnNonZeroExitCode=False,outputToStdout=False)
            return exitcode == 0
        elif o.system.platformtype.isSolaris() or o.system.platformtype.isDarwin():
            command = "netstat -an -f inet"
            (exitcode, output) = o.system.process.execute(command, dieOnNonZeroExitCode=False,outputToStdout=False)
            for line in output.splitlines():
                match = re.match(".*\.%s .*\..*LISTEN"%port, line)
                if match:
                    return True
            # No ipv4? Then check ipv6
            command = "netstat -an -f inet6"
            (exitcode, output) = o.system.process.execute(command, dieOnNonZeroExitCode=False,outputToStdout=False)
            for line in output.splitlines():
                match = re.match(".*\.%s .*\..*LISTEN"%port, line)
                if match:
                    return True
            return False
        elif o.system.platformtype.isWindows():
            # We use the GetTcpTable function of the Windows IP Helper API (iphlpapi.dll)
            #
            # Parameters of GetTcpTable:
            #    - A buffer receiving the table.
            #    - An integer indicating the length of the buffer. This value will be overwritten with the required buffer size, if the buffer isn't large enough.
            #    - A boolean indicating if the table should be sorted.
            #
            # Microsoft reference: http://msdn2.microsoft.com/en-us/library/aa366026(VS.85).aspx
            # Python example code: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/392572

            import ctypes, socket
            DWORD = ctypes.c_ulong
            MIB_TCP_STATE_LISTEN = 2
            dwSize = DWORD(0)

            # Retrieve the size of the TCP table, to create a structure with the right size.
            # We do this by calling the GetTcpTable function and passing an empty buffer.
            # Because the buffer is too small, the dwSize variable will be overwritten with the required buffer size.
            ctypes.windll.iphlpapi.GetTcpTable("", ctypes.byref(dwSize), 0)

            # Define MIB (Management Information Base) classes
            class MIB_TCPROW(ctypes.Structure):
                _fields_ = [('dwState', DWORD),
                            ('dwLocalAddr', DWORD),
                            ('dwLocalPort', DWORD),
                            ('dwRemoteAddr', DWORD),
                            ('dwRemotePort', DWORD)]

            class MIB_TCPTABLE(ctypes.Structure):
                _fields_ = [('dwNumEntries', DWORD),
                            ('table', MIB_TCPROW * dwSize.value)]

            tcpTable = MIB_TCPTABLE()  # Initialize the buffer that will retrieve the TCP table
            tcpTable.dwNumEntries = 0

            # Call the GetTcpTable function again, but now with a buffer that's large enough. The TCP table will be written in the buffer.
            retVal = ctypes.windll.iphlpapi.GetTcpTable(ctypes.byref(tcpTable), ctypes.byref(dwSize), 0)
            if not retVal == 0:
                raise RuntimeError("o.system.net.checkListenPort: The function iphlpapi.GetTcpTable returned error number %s"%retVal)

            for i in range(tcpTable.dwNumEntries):  # We can't iterate over the table the usual way as tcpTable.table isn't a Python table structure.
                tcpState = tcpTable.table[i].dwState
                tcpLocalPort = socket.ntohs(tcpTable.table[i].dwLocalPort) # socket.ntohs() convert a 16-bit integer from network to host byte order.
                if tcpState == MIB_TCP_STATE_LISTEN and tcpLocalPort == port:
                    return True
            return False # The port is not in a listening state.

        else:
            raise RuntimeError("This platform is not supported in o.system.net.checkListenPort()")

    def getNameServer(self):
        """Returns the first nameserver IP found in /etc/resolv.conf

        Only implemented for Unix based hosts.

        @returns: Nameserver IP
        @rtype: string

        @raise NotImplementedError: Non-Unix systems
        @raise RuntimeError: No nameserver could be found in /etc/resolv.conf
        """
        if o.system.platformtype.isUnix():
            nameserverlines = o.codetools.regex.findAll(
            "^\s*nameserver\s+(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s*$",
            o.system.fs.fileGetContents('/etc/resolv.conf'))

            if not nameserverlines:
                raise RuntimeError('No nameserver found in /etc/resolv.conf')

            nameserverline = nameserverlines[0]
            return nameserverline.strip().split(' ')[-1]
        elif o.system.platformtype.isWindows():
            import wmi
            w=wmi.WMI()
            for nicCfg in w.Win32_NetworkAdapterConfiguration():
                if nicCfg.DNSServerSearchOrder:
                    return str(nicCfg.DNSServerSearchOrder[0])
        else:
            raise NotImplementedError('This function is only supported on Unix/Windows systems')

    def getIpAddresses(self,up=False):
        nics=self.getNics(up)
        result=[]
        for nic in nics:
            ipTuple = self.getIpAddress(nic)
            if ipTuple: # if empty array skip
                result.extend([ ip[0] for ip in ipTuple])
        return result
    
    def checkIpAddressIsLocal(self,ipaddr):
        if ipaddr.strip() in self.getIpAdresses():
            return True
        else:
            return False

    def enableProxy(self):
        maincfg = o.config.getConfig('main')
        if 'proxy' in maincfg:
            import os, urllib2
            proxycfg = maincfg['proxy']
            proxyserver = proxycfg['server']
            params = ""
            proxyuser =  proxycfg.get('user')
            if proxyuser:
                params += proxyuser
                proxypassword = proxycfg.get('password')
                if proxypassword:
                    params += ":%s" % proxypassword
                params += "@"
            params += proxyserver
            if pymonkey.o.system.platformtype.isUnix():
                os.environ['http_proxy'] = proxyserver
            proxy_support = urllib2.ProxyHandler()
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
    
    def getNics(self,up=False):
        """ Get Nics on this machine
        Works only for Linux/Solaris systems
        @param up: only returning nics which or up
        """
        niclist = []
        regex = ''
        output = ''
        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            exitcode,output = o.system.process.execute("ip l", outputToStdout=False)
            if not up:
                regex = "^\d+:\s(?P<name>[\w\d]*):.*$"
            else:
                regex = "^\d+:\s(?P<name>[\w\d]*):\s<.*UP.*>.*$"
            return list(set(re.findall(regex,output,re.MULTILINE)))
        elif o.system.platformtype.isSolaris():
            exitcode,output = o.system.process.execute("ifconfig -a", outputToStdout=False)
            if up:
                regex = "^([\w:]+):\sflag.*<.*UP.*>.*$"
            else:
                regex = "^([\w:]+):\sflag.*$"
            nics = set(re.findall(regex,output,re.MULTILINE))
            exitcode,output = o.system.process.execute("dladm show-phys", outputToStdout=False)
            lines = output.splitlines()
            for line in lines[1:]:
                nic = line.split()
                if up:
                    if nic[2] == 'up':
                        nics.add(nic[0])
                else:
                    nics.add(nic[0])
            return list(nics)
        elif o.system.platformtype.isWindows():
            import wmi
            w = wmi.WMI()
            return [ "%s:%s" %(ad.index,str(ad.NetConnectionID)) for ad in w.Win32_NetworkAdapter() if ad.PhysicalAdapter and ad.NetEnabled]
        else:
            raise RuntimeError("Not supported on this platform!")

    def getNicType(self,interface):
        """ Get Nic Type on a certain interface
        @param interface: Interface to determine Nic type on
        @raise RuntimeError: On linux if ethtool is not present on the system
        """
        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            output=''
            if o.system.fs.exists("/sys/class/net/%s"%interface):
                output = o.system.fs.fileGetContents("/sys/class/net/%s/type"%interface)
            if output.strip() == "32":
                return "INFINIBAND"
            else:
                if o.system.fs.exists('/proc/net/vlan/%s'%(interface)):
                    return 'VLAN'
                exitcode,output = o.system.process.execute("which ethtool", False, outputToStdout=False)
                if exitcode != 0:
                    raise RuntimeError("Ethtool is not installed on this system!")
                exitcode,output = o.system.process.execute("ethtool -i %s"%(interface),False,outputToStdout=False)
                if exitcode !=0:
                    return 'VIRTUAL'
                match = re.search("^driver:\s+(?P<driver>\w+)\s*$",output,re.MULTILINE)
                if match and match.group("driver") == "tun" :
                    return "VIRTUAL"
                if match and match.group("driver") == "bridge" :
                    return "VLAN"
                return "ETHERNET_GB"
        elif o.system.platformtype.isSolaris():
            command = "ifconfig %s"%interface
            exitcode,output = o.system.process.execute(command, outputToStdout=False, dieOnNonZeroExitCode=False)
            if exitcode != 0:
                # temporary plumb the interface to lookup its mac
                o.logger.log("Interface %s is down. Temporarily plumbing it to be able to lookup its nic type" % interface, 1)
                o.system.process.execute('%s plumb' % command, outputToStdout=False)
                (exitcode, output) = o.system.process.execute(command, outputToStdout=False)
                o.system.process.execute('%s unplumb' % command, outputToStdout=False)
            if output.find("ipib") >=0:
                return "INFINIBAND"
            else:
                #work with interfaces which are subnetted on vlans eq e1000g5000:1
                interfacepieces = interface.split(':')
                interface = interfacepieces[0]
                match = re.search("^\w+?(?P<interfaceid>\d+)$",interface,re.MULTILINE)
                if not match:
                    raise ValueError("Invalid interface %s"%(interface))
                if len(match.group('interfaceid')) >= 4:
                    return "VLAN"
                else:
                    if len(interfacepieces) > 1:
                        return "VIRTUAL"
                    else:
                        return "ETHERNET_GB"
        elif o.system.platformtype.isWindows():
            if o.system.net.getVlanTagFromInterface(interface) > 0:
                return "VLAN"
            else:
                import wmi
                w = wmi.WMI()
                NICIndex = interface.split(":")[0]
                nic = w.Win32_NetworkAdapter(index=NICIndex)[0]
                if hasattr(nic, 'AdapterTypeId'):
                    if nic.AdapterTypeId == 0:
                        return "ETHERNET_GB"
                    elif nic.AdapterTypeId == 15:
                        return "VIRTUAL"
                    else:
                        return "UNKNOWN"
                else:
                    return "UNKNOWN"
        else:
            raise RuntimeError("Not supported on this platform!")

    def getVlanTag(self,interface,nicType=None):
        """Get VLan tag on the specified interface and vlan type"""
        if nicType == None:
            nicType=o.system.net.getNicType(interface)
        if nicType == "INFINIBAND" or nicType=="ETHERNET_GB" or nicType == "VIRTUAL":
            return "0"
        if o.system.platformtype.isLinux():
            #check if its a vlan
            vlanfile = '/proc/net/vlan/%s'%(interface)
            if o.system.fs.exists(vlanfile):
                return o.system.net.getVlanTagFromInterface(interface)
            bridgefile = '/sys/class/net/%s/brif/'%(interface)
            for brif in o.system.fs.listDirsInDir(bridgefile):
                brif = o.system.fs.getBaseName(brif)
                vlanfile = '/proc/net/vlan/%s'%(brif)
                if o.system.fs.exists(vlanfile):
                    return o.system.net.getVlanTagFromInterface(brif)
            return "0"
        elif o.system.platformtype.isSolaris() or o.system.platformtype.isWindows():
            return o.system.net.getVlanTagFromInterface(interface)
        else:
            raise RuntimeError("Not supported on this platform!")

    def getVlanTagFromInterface(self,interface):
        """Get vlan tag from interface
        @param interface: string interface to get vlan tag on
        @rtype: integer representing the vlan tag
        """
        if o.system.platformtype.isLinux():
            vlanfile = '/proc/net/vlan/%s'%(interface)
            if o.system.fs.exists(vlanfile):
                content = o.system.fs.fileGetContents(vlanfile)
                match = re.search("^%s\s+VID:\s+(?P<vlantag>\d+)\s+.*$"%(interface),content,re.MULTILINE)
                if match:
                    return match.group('vlantag')
                else:
                    raise ValueError("Could not find vlantag for interface %s"%(interface))
            else:
                raise ValueError("This is not a vlaninterface %s"%(interface))
        elif o.system.platformtype.isSolaris():
            #work with interfaces which are subnetted on vlans eq e1000g5000:1
            interface = interface.split(':')[0]
            match = re.search("^\w+?(?P<interfaceid>\d+)$",interface,re.MULTILINE)
            if not match:
                raise ValueError("This is not a vlaninterface %s"%(interface))
            return int(match.group('interfaceid'))/1000
        elif o.system.platformtype.isWindows():
            import wmi
            vir = wmi.WMI(namespace='virtualization')
            mac = o.system.net.getMacAddress(interface)
            mac = mac.replace(":","")
            dynFor = vir.Msvm_DynamicForwardingEntry(elementname=mac)
            return dynFor[0].VlanId if dynFor else 0

    def getReachableIpAddress(self, ip, port):
        """Returns the first local ip address that can connect to the specified ip on the specified port"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((ip, port))
        except:
            raise RuntimeError("No ip foungetIpAddressd that can connect to %s:%s"%(ip,port))
        return s.getsockname()[0]

    def getNetworkInfo(self):
        """
        returns {macaddr_name:[ipaddr,ipaddr],...}
        """ 
        netaddr={}       
        nics=self.getNics()
        for nic in nics:
            mac=self.getMacAddress(nic)
            ips=[item[0] for item in self.getIpAddress(nic)]
            netaddr["%s_%s"%(mac,nic.lower())]=ips            
        return  netaddr

    def getIpAddress(self, interface):
        """Return a list of ip addresses and netmasks assigned to this interface"""
        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            command = "ip a s %s" % interface
            (exitcode, output) = o.system.process.execute(command, outputToStdout=False, dieOnNonZeroExitCode=False)
            if exitcode != 0:
                return []
            nicinfo = re.findall("^\s+inet\s+(.*)\/(\d+)\s(?:brd\s)?(\d+\.\d+\.\d+\.\d+)?\s?scope.*$",output,re.MULTILINE)
            result = []
            for ipinfo in nicinfo:
                ip = ipinfo[0]
                masknumber = int(ipinfo[1])
                broadcast = ipinfo[2]
                mask = ""
                for i in range(4):
                    mask += str(int(hex(pow(2,32)-pow(2,32-masknumber))[2:][i*2:i*2+2],16)) + "."
                result.append([ip, mask[:-1], broadcast])
            return result
        elif o.system.platformtype.isSolaris():
            command = "ifconfig %s"%(interface)
            (exitcode, output) = o.system.process.execute(command, outputToStdout=False, dieOnNonZeroExitCode=False)
            if exitcode != 0:
                return []
            result = []
            match = re.search("^\s+inet\s+(?P<ipaddress>[\d\.]+)\s+.*netmask\s+(?P<netmask>[a-f\d]{8})\s?(broadcast)?\s?(?P<broadcast>[\d\.]+)?$", output, re.MULTILINE)
            if not match:
                return []
            ip = match.group('ipaddress')
            netmaskhex = match.group('netmask')
            broadcast = match.group('broadcast')
            mask =""
            for j in range(4):
                mask += str(int(netmaskhex[j*2:j*2+2], 16)) + "."
            return [[ip , mask[:-1], broadcast]]
        elif o.system.platformtype.isWindows():
            import wmi
            ipv4Pattern = '^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
            
            w = wmi.WMI()
            NICIndex = interface.split(":")[0]
            nic = w.Win32_NetworkAdapterConfiguration(index=NICIndex)[0]
            result = []
            if nic.IPAddress:
                for x in range(0, len(nic.IPAddress)):
                    # skip IPv6 addresses for now
                    if re.match(ipv4Pattern, str(nic.IPAddress[x])) != None: 
                        result.append( [str(nic.IPAddress[x]), str(nic.IPSubnet[x]), ''] )
            return result
        else:
            raise RuntimeError("o.system.net.getIpAddress not supported on this platform")

    def getMacAddress(self, interface):
        """Return the MAC address of this interface"""
        if not interface in self.getNics():
            raise LookupError("Interface %s not found on the system" % interface)
        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            if o.system.fs.exists("/sys/class/net"):
                return o.system.fs.fileGetContents('/sys/class/net/%s/address' % interface).strip()
            else:
                command = "ifconfig %s | grep HWaddr| awk '{print $5}'"% interface
                (exitcode,output)=o.system.process.execute(command, outputToStdout=False)
                return self.pm_formatMacAddress(output)
        elif o.system.platformtype.isSolaris():
            # check if interface is a logical inteface ex: bge0:1
            tokens = interface.split(':')
            if len(tokens) > 1 :
                interface = tokens[0]
            command = "ifconfig %s" % interface
            (exitcode, output) = o.system.process.execute(command, outputToStdout=False, dieOnNonZeroExitCode=False)
            if exitcode != 0:
                # temporary plumb the interface to lookup its mac
                o.logger.log("Interface %s is down. Temporarily plumbing it to be able to lookup its MAC address" % interface, 1)
                o.system.process.execute('%s plumb' % command, outputToStdout=False)
                (exitcode, output) = o.system.process.execute(command, outputToStdout=False, dieOnNonZeroExitCode=False)
                o.system.process.execute('%s unplumb' % command, outputToStdout=False)
            if exitcode == 0:
                match = re.search(r"^\s*(ipib|ether)\s*(?P<mac>\S*)", output, re.MULTILINE)
                if match:
                    return self.pm_formatMacAddress(match.group("mac"))
            return None
        elif o.system.platformtype.isWindows():
			import wmi
			w = wmi.WMI()	
			NICIndex = interface.split(":")[0]
			return str(w.Win32_NetworkAdapterConfiguration(index=NICIndex)[0].MACAddress)
        else:
            raise RuntimeError("o.system.net.getMacAddress not supported on this platform")

    def pm_formatMacAddress(self, macaddress):
        macpieces = macaddress.strip().split(':')
        mac = ""
        for piece in macpieces:
            if len(piece)==1:
                mac += "0"
            mac += piece + ":"
        mac = mac[:-1]
        return mac

    def isIpInDifferentNetwork(self, ipaddress):
        for nic in o.system.net.getNics():
            for ip in o.system.net.getIpAddress(nic):
                if openwizzy.pmtypes.IPv4Address(ipaddress) in openwizzy.pmtypes.IPv4Range(netIp=ip[0], netMask=ip[1]):
                    return False
        return True

    def getMacAddressForIp(self, ipaddress):
        """Search the MAC address of the given IP address in the ARP table

        @param ipaddress: IP address of the machine
        @rtype: string
        @return: The MAC address corresponding with the given IP
        @raise: RuntimeError if no MAC found for IP or if platform is not suppported
        """
        def doArp(ipaddress):
            args = list()
            if o.system.platformtype.isLinux():
                # We do not want hostnames to show up in the ARP output
                args.append("-n")

            return o.system.process.execute(
                'arp %s %s' % (" ".join(args), ipaddress),
                dieOnNonZeroExitCode=False,
                outputToStdout=False
            )

        def noEntry(output):
            return ("no entry" in output) or ("(incomplete)" in output)

        if o.system.platformtype.isUnix():
            if self.isIpInDifferentNetwork(ipaddress):
                warning = 'The IP address %s is from a different subnet. This means that the macaddress will be the one of the gateway/router instead of the correct one.'
                o.errorconditionhandler.raiseWarning(warning % ipaddress)

            exitcode, output = doArp(ipaddress)
            # Output of arp is 1 when no entry found is 1 on solaris but 0
            # on Linux, so we check the actual output
            if noEntry(output):
                # ping first and try again
                self.pingMachine(ipaddress, pingtimeout=1)
                exitcode, output = doArp(ipaddress)

            if not noEntry(output) and o.system.platformtype.isSolaris():
                mac = output.split()[3]
                return self.pm_formatMacAddress(mac)
            else:
                mo = re.search("(?P<ip>[0-9]+(.[0-9]+){3})\s+(?P<type>[a-z]+)\s+(?P<mac>([a-fA-F0-9]{2}[:|\-]?){6})",output)
                if mo:
                    return self.pm_formatMacAddress(mo.groupdict()['mac'])
                else:
                    # On Linux the arp will not show local configured ip's in the table.
                    # That's why we try to find the ip with "ip a" and match for the mac there.

                    output, stdout, stderr = o.system.process.run('ip a', stopOnError=False)
                    if exitcode:
                        raise RuntimeError('Could not get the MAC address for [%s] because "ip" is not found'%s)
                    mo = re.search('\d:\s+\w+:\s+.*\n\s+.+\s+(?P<mac>([a-fA-F0-9]{2}[:|\-]?){6}).+\n\s+inet\s%s[^0-9]+'%ipaddress, stdout, re.MULTILINE)
                    if mo:
                        return self.pm_formatMacAddress(mo.groupdict()['mac'])
            raise RuntimeError("MAC address for [%s] not found"%ipaddress)
        else:
            raise RuntimeError("o.system.net.getMacAddressForIp not supported on this platform")

    def getHostname(self):
        """Get hostname of the machine
        """
        return socket.gethostname()

    def isNicConnected(self,interface):
        if o.system.platformtype.isLinux():
            carrierfile = '/sys/class/net/%s/carrier'%(interface)
            if not o.system.fs.exists(carrierfile):
                return False
            try:
                return int(o.system.fs.fileGetContents(carrierfile)) != 0
            except IOError:
                return False
        elif o.system.platformtype.isESX():
            nl = o.system.net.getNics(up=True)
            if interface not in nl:
                return False
            else:
                return True
        elif o.system.platformtype.isSolaris():
            if o.system.platformtype.getVersion() < 100:
                command = "dladm show-dev -p -o STATE %s" % interface
                expectResults = ['STATE="up"', 'STATE="unknown"']
            else:
                command = "dladm show-phys -p -o STATE %s" % interface
                expectResults = ['up', 'unknown']

            (exitcode, output) = o.system.process.execute(command, dieOnNonZeroExitCode=False, outputToStdout=False)
            if exitcode != 0:
                return False
            output = output.strip()
            if output in expectResults:
                return True
            else:
                return False

    def getHostByName(self, dnsHostname):
        import socket
        return socket.gethostbyname(dnsHostname)
    def getDefaultRouter(self):
        """Get default router
        @rtype: string representing the router interface
        """
        if o.system.platformtype.isLinux() or o.system.platformtype.isESX():
            command = "ip r | grep 'default' | awk {'print $3'}"
            (exitcode, output) = o.system.process.execute(command, outputToStdout=False)
            return output.strip()
        elif o.system.platformtype.isSolaris():
            command = "netstat -rn | grep default | awk '{print $2}'"
            (exitcode, output) = o.system.process.execute(command, outputToStdout=False)
            return output.strip()
        else:
            raise RuntimeError("o.system.net.getDefaultRouter not supported on this platform")

    def validateIpAddress(self, ipaddress):
        """Validate wether this ip address is a valid ip address of 4 octets ranging from 0 to 255 or not
        @param ipaddress: ip address to check on
        @rtype: boolean...True if this ip is valid, False if not
        """
        if len(ipaddress.split()) == 1:
            ipList = ipaddress.split('.')
            if len(ipList) == 4:
                for i, item in enumerate(ipList):
                    try:
                        ipList[i] = int(item)
                    except:
                        return False
                    if not isinstance(ipList[i], int):
                        o.logger.log('[%s] is not a valid ip address, octects should be integers'%ipaddress, 7)
                        return False
                if max(ipList) < 256:
                    o.logger.log('[%s] is a valid ip address'%ipaddress, 9)
                    return True
                else:
                    o.logger.log('[%s] is not a valid ip address, octetcs should be less than 256'%ipaddress, 7)
                    return False
            else:
                o.logger.log('[%s] is not a valid ip address, ip should contain 4 octets'%ipaddress, 7)
                return False
        else:
            o.logger.log('[%s] is not a valid ip address'%ipaddress, 7)
            return False

    def pingMachine(self, ip, pingtimeout=60, recheck = False, allowhostname = False):
        """Ping a machine to check if it's up/running and accessible
        @param ip: Machine Ip Address
        @param pingtimeout: time in sec after which ip will be declared as unreachable
        @param recheck: Unused, kept for backwards compatibility
        @param allowhostname: allow pinging on hostname (default is false)
        @rtype: True if machine is pingable, False otherwise
        """
        if not allowhostname:
            if not o.system.net.validateIpAddress(ip):
                raise ValueError('ERROR: invalid ip address passed:[%s]'%ip)

        o.logger.log('pingMachine %s, timeout=%d, recheck=%s' % (ip, pingtimeout, str(recheck)), 8)

        start = time.time()
        pingsucceeded = False
        while time.time() - start < pingtimeout:
            if o.system.platformtype.isSolaris():
                #ping -c 1 IP 1
                #Last 1 is timeout in seconds
                exitcode, output = o.system.process.execute(
                                    'ping -c 1 %s 1' % ip, False, False)
            elif o.system.platformtype.isLinux():
                #ping -c 1 -W 1 IP
                exitcode, output = o.system.process.execute(
                                    'ping -c 1 -W 1 -w 1 %s' % ip, False, False)
            elif o.system.platformtype.isUnix():
                exitcode, output = o.system.process.execute('ping -c 1 %s'%ip, False, False)
            elif o.system.platformtype.isWindows():
                exitcode, output = o.system.process.execute('ping -w %d %s'%(pingtimeout, ip), False, False)
            else:
                raise RuntimeError('Platform is not supported')
            if exitcode == 0:
                pingsucceeded = True
                o.logger.log('Machine with ip:[%s] is pingable'%ip, 9)
                return True
            time.sleep(1)
        if not pingsucceeded:
            o.logger.log("Could not ping machine with ip:[%s]"%ip, 7)
            return False


    def isIpInHostsFile(self, hostsfile, ip):
        """Check if ip is in the hostsfile
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to check
        """
        # get content of hostsfile
        filecontents = o.system.fs.fileGetContents(hostsfile)
        res = re.search('^%s\s' %ip, filecontents, re.MULTILINE)
        if res:
            return True
        else:
            return False

    def removeFromHostsFile(self, hostsfile, ip):
        """Update a hostfile, delete ip from hostsfile
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to remove
        """
        o.logger.log('Updating hosts file %s: Removing %s' % (hostsfile, ip), 8)
        # get content of hostsfile
        filecontents = o.system.fs.fileGetContents(hostsfile)
        searchObj = re.search('^%s\s.*\n' %ip, filecontents, re.MULTILINE)
        if searchObj:
            filecontents = filecontents.replace(searchObj.group(0), '')
            o.system.fs.writeFile(hostsfile, filecontents)
        else:
            o.logger.log('Ip address %s not found in hosts file' %ip, 1)
            
    def getHostNamesForIP(self, hostsfile, ip):
        """Get hostnames for ip address
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to get hostnames from
        @return: List of machinehostnames
        """
        o.logger.log('Get hostnames from hosts file %s for ip %s' % (hostsfile, ip), 8)
        # get content of hostsfile
        if self.isIpInHostsFile(hostsfile, ip):
            filecontents = o.system.fs.fileGetContents(hostsfile)
            searchObj = re.search('^%s\s.*\n' %ip, filecontents, re.MULTILINE)
            hostnames = searchObj.group(0).strip().split()
            hostnames.pop(0)
            return hostnames
        else:
            return []

    def updateHostsFile(self,hostsfile,ip,hostname):
        """Update a hostfile to contain the basic information install
        @param hostsfile: File where hosts are defined
        @param ip: Ip of the machine to add/modify
        @param hostname: List of machinehostnames to add/modify
        """
        if isinstance(hostname, str):
            hostname = hostname.split()
        o.logger.log('Updating hosts file %s: %s -> %s' % (hostsfile, hostname, ip), 8)
        # get content of hostsfile
        filecontents = o.system.fs.fileGetContents(hostsfile)
        searchObj = re.search('^%s\s.*\n' %ip, filecontents, re.MULTILINE)
        
        hostnames = ' '.join(hostname)
        if searchObj:
            filecontents = filecontents.replace(searchObj.group(0), '%s %s\n' %(ip, hostnames))
        else:
            filecontents += '%s %s\n' %(ip, hostnames)

        o.system.fs.writeFile(hostsfile, filecontents)


    def download(self, url, localpath, username=None, passwd=None):
        '''Download a url to a file or a directory, supported protocols: http, https, ftp, file
        @param url: URL to download from
        @type url: string
        @param localpath: filename or directory to download the url to
        @type localpath: string
        @param username: username for the url if it requires authentication
        @type username: string
        @param passwd: password for the url if it requires authentication
        @type passwd: string
        '''
        if not url:
            raise ValueError('URL can not be None or empty string')
        if not localpath:
            raise ValueError('Local path to download the url to can not be None or empty string')
        filename = ''
        if o.system.fs.isDir(localpath):
            filename = o.system.fs.joinPaths(localpath, o.system.fs.getBaseName(url))
        else:
            if o.system.fs.isDir(o.system.fs.getDirName(localpath)) and not o.system.fs.exists(localpath):
                filename = localpath
            else:
                raise ValueError('Local path is an invalid path')
        o.logger.log('Downloading url %s to local path %s'%(url, filename), 4)

        from urllib import FancyURLopener, splittype
        class myURLOpener(FancyURLopener):
            # read a URL, with automatic HTTP authentication
            def __init__(self, user, passwd):
                self._user = user
                self._passwd = passwd
                self._promptcalled = False
                FancyURLopener.__init__(self)

            def prompt_user_passwd(self, host, realm):
                if not self._user or not self._passwd:
                    raise RuntimeError('Server requested authentication but nothing was given')
                if not self._promptcalled:
                    self._promptcalled = True
                    return self._user, self._passwd
                raise RuntimeError('Could not authenticate with the given authentication user:%s and password:%s'%(self._user, self._passwd))

        urlopener = myURLOpener(username, passwd)
        if username and passwd and splittype(url)[0] == 'ftp':
            url = url.split('://')[0]+'://%s:%s@'%(username,passwd)+url.split('://')[1]
        urlopener.retrieve(url, filename, None, None)
        o.logger.log('URL %s is downloaded to local path %s'%(url, filename), 4)

    def getDomainName(self):
        """
        Retrieve the dns domain name
        """
        cmd = "dnsdomainname" if o.system.platformtype.isLinux() else "domainname" if o.system.platformtype.isSolaris() else ""
        if not cmd:
            raise PlatformNotSupportedError('Platform "%s" is not supported. Command is only supported on Linux and Solaris' % o.system.platformtype.name)

        exitCode, domainName = o.system.process.execute(cmd, outputToStdout=False)

        if not domainName:
            raise ValueError('Failed to retrieve domain name')

        domainName = domainName.splitlines()[0]

        return domainName

class PlatformNotSupportedError(RuntimeError): pass

class NetworkZone:
    ipRanges=None ##array(IPRange)
