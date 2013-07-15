# import socket
from OpenWizzy import o
import time
# q=openwizzy.q

ZDaemonClientClass=o.core.grid.getZDaemonClientClass()

class LogTargetClientDaemon(ZDaemonClientClass):
    """Forwards incoming logRecords to localclientdaemon"""
    def __init__(self, serverip=None):
        self.connected = False
        if serverip==None:
            serverip="127.0.0.1"
        self.serverip = serverip
        enabled = self.checkTarget()
        self.enabled=False
        self.retry=True
        if enabled:
            self.loggerClient=o.core.grid.getZLoggerClient(ipaddr=serverip)
            self.enabled=True

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if not o.system.platform.ubuntu.check(False):
            wait=True
            end=o.base.time.getTimeEpoch()+60
            while wait:
                wait=o.system.net.tcpPortConnectionTest(self.serverip,4444)==False
                if wait and o.base.time.getTimeEpoch()>end:
                    o.errorconditionhandler.raiseOperationalWarning(msgpub="cannot find local client daemon, cannot connect",message="",category="grid.startup",tags="")
                    return False
                print "try to connect to clientdaemon, will try for 60 sec."
                time.sleep(1)
        o.logger.clientdaemontarget=self
        return True

    def __str__(self):
        """ string representation of a LogTargetServer to ES"""
        return 'LogTargetLogServer logging to %s' % (str(self.serverip))

    __repr__ = __str__


    def log(self, log):
        """
        forward the already encoded message to the target destination

        """
        if self.enabled:
            self.loggerClient.logMessage(log.toJson())
        # else:
        #     if o.logger.logTargets==[]:  #otherwise all logmessages in this phase would go unnoticed
        #         print log  

