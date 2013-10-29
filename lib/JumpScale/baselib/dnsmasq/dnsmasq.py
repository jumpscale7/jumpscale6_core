from JumpScale import j

class DNSMasq(object):

    def __init__(self, config_path=None):
        if not config_path:
            self._configfile = j.system.fs.joinPaths('/etc', 'dnsmasq.conf')
        else:
            self._configfile = config_path
        if not j.system.platform.ubuntu.findPackagesInstalled('dnsmasq'):
            j.system.platform.ubuntu.install('dnsmasq')

    @property
    def configpath(self):
        return self._configfile

    @configpath.setter
    def configpath(self, value):
        self._configfile = value

    def addHost(self, macaddress, ipaddress, name=None):
        """Adds a dhcp-host entry to dnsmasq.conf file"""
        te = j.codetools.getTextFileEditor(self._configfile)
        contents = 'dhcp-host=%s' % macaddress
        if name:
            contents += ',%s' % name
        contents += ',%s\n' % ipaddress
        te.appendReplaceLine('.*%s.*' % macaddress, contents)
        te.save()
        self.restart()

    def removeHost(self, macaddress):
        """Removes a dhcp-host entry from dnsmasq.conf file"""
        te = j.codetools.getTextFileEditor(self._configfile)
        te.deleteLines('.*%s.*' % macaddress)
        te.save()
        self.restart()

    def configureIPRange(self, startIP, endIP, netmask):
        '''Configures IP range for a dhcp-host'''
        content = 'dhcp-range=%s,%s,%s' % (startIP, endIP, netmask)
        te = j.codetools.getTextFileEditor(self._configfile)
        te.appendLine(content)
        te.save()
        self.restart()

    def restart(self):
        """Restarts dnsmasq"""
        j.system.process.execute('/etc/init.d/dnsmasq restart')

    def reload(self):
        pass