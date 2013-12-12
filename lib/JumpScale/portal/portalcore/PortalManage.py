from JumpScale import j
import JumpScale.baselib.inifile
import os
from PortalProcess import PortalProcess


class Group():
    pass


class PortalManage():

    """
    management class for appserver
    """

    def startprocess(self, processNr=1, reset=False,port=8081):
        """
        """
        j.apps = Group()
        j.db.keyvaluestore
        self._initPortal()
        j.core.portal.runningPortal.start(reset=reset)

    def _initPortal(self, processNr=1):

        ini = j.tools.inifile.open(os.path.abspath("cfg/appserver.cfg"))
        appdir = ini.getValue("main", "appdir")

        cfgdir = j.system.fs.joinPaths(j.system.fs.getcwd(), "cfg")
        curdir = j.system.fs.getcwd()

        j.system.fs.changeDir(appdir)

        #self.masterIP=self.gridInifile.getValue("master", "ip")
        #self.masterSecret=self.gridInifile.getValue("master", "secret")
        #self.masterPort=self.gridInifile.getValue("master", "port")

        try:
            ips = j.system.net.getIpAddresses()
        except:
            print "WARNING, COULD NOT FIND LOCAL IP ADDRESSES, use value from appserver config file"  # @todo implement on windows
            ips = list()

        ips = [item for item in ips if item != "127.0.0.1"]
        if len(ips) == 1:
            ini.setParam('main', "ipaddr", ips[0])
            ip = ips[0]
        elif len(ips) == 0:
            ip = ini.getValue("main", "ipaddr")
        else:
            pass
            # ip = ",".join(ips)
            # ini.setParam('main', "ipaddr", ip)

        PortalProcess(processNr=processNr, cfgdir=cfgdir, startdir=curdir)


