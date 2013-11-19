# import socket
from JumpScale import j
import JumpScale.grid
import time

class LogTargetLogForwarder():
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

        if j.system.net.tcpPortConnectionTest(self.serverip,4443)==False:
            print "will be waiting for 10 sec if I an reach local logger."
        if j.system.net.waitConnectionTest(self.serverip,4443,10)==False:
            raise RuntimeError("Could not reach local logserver")
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
