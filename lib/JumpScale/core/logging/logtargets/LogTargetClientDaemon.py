# import socket
from JumpScale import j
import time

class LogTargetClientDaemon():
    """Forwards incoming logRecords to localclientdaemon"""
    def __init__(self, serverip=None):
        self.connected = False
        if serverip==None:
            serverip="127.0.0.1"
        self.serverip = serverip
        self.checkTarget()

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if not j.system.platform.ubuntu.check(False):
            wait=True
            end=j.base.time.getTimeEpoch()+60
            while wait:
                wait=j.system.net.tcpPortConnectionTest(self.serverip,4444)==False
                if wait and j.base.time.getTimeEpoch()>end:
                    j.errorconditionhandler.raiseOperationalWarning(msgpub="cannot find local client daemon, cannot connect",message="",category="grid.startup",tags="")
                    return False
                print "try to connect to clientdaemon, will try for 60 sec."
                time.sleep(1)
        
        self.loggerClient=j.core.grid.getZLoggerClient(ipaddr=self.serverip)
        self.enabled=True
        j.logger.clientdaemontarget=self
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
            # print "LOG:%s"%log
            self.loggerClient.log(log)
        # else:
        #     if j.logger.logTargets==[]:  #otherwise all logmessages in this phase would go unnoticed
        #         print log  

