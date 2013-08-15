
from OpenWizzy import o
import OpenWizzy.grid
import OpenWizzy.baselib.key_value_store
import time
from OpenWizzy.grid.grid.ZDaemon import ZDaemonCMDS

    
class MasterServerCmds(ZDaemonCMDS):
    def __init__(self,daemon=None):
        self.db=o.db.keyvaluestore.getFileSystemStore("master") #will serialize in ujson
        # self.db=o.db.keyvaluestore.getLevelDBStore('DFSIO_%s'%nsid, '/opt/openwizzy6/var/db/leveldb')

    def gridNew(self):
        return 1

class MasterServer():

    def __init__(self,port=7788):
        self.daemon=o.core.grid.getZDaemon(port=port,nrCmdGreenlets=100)
        self.daemon.setCMDsInterface(MasterServerCmds)  #pass as class not as object !!!

    def start(self):
        self.daemon.start()


ZDaemonClientClass=o.core.grid.getZDaemonClientClassAutoGen()

# o.logger.consoleloglevel=6

class MasterClient(ZDaemonClientClass):
    def __init__(self,ipaddr):
        ZDaemonClientClass.__init__(self,ipaddr=ipaddr,port=443)


class MasterServerFactory():
    def getserver(self,port=443):
        return MasterServer(port)

    def getclient(self,ipaddr="127.0.0.1"):
        return MasterClient(ipaddr)

    def getCmdClassServer(self):
        """
        is for test purposes, can directly operate the cmds to test
        """
        return MasterServerCmds
        
