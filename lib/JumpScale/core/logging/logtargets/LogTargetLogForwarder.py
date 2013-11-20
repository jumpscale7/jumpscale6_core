# import socket
from JumpScale import j
import time


TIMEOUT = 5

class LogTargetLogForwarder():
    """Forwards incoming logRecords to localclientdaemon"""
    def __init__(self, serverip=None):
        self._lastcheck = 0
        self.connected = False
        self.enabled = True
        if not serverip:
            if j.application.config.exists('grid.master.ip'):
                serverip = j.application.config.get("grid.master.ip")
            if not serverip:
                self.enabled = False
                return
        self.serverip = serverip
        self.checkTarget()

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        if self._lastcheck + TIMEOUT > time.time():
            return self.connected
        self.connected = j.system.net.tcpPortConnectionTest(self.serverip,4443)
        self._lastcheck = time.time()
        if not self.connected:
            print "will be waiting for 5 sec if I an reach local logger."
            return self.connected

        import JumpScale.grid
        self.loggerClient=j.core.grid.getZLoggerClient(ipaddr=self.serverip)
        j.logger.clientdaemontarget=self
        return self.connected

    def __str__(self):
        """ string representation of a LogTargetServer to ES"""
        return 'LogTargetLogServer logging to %s' % (str(self.serverip))

    __repr__ = __str__


    def log(self, log):
        """
        forward the already encoded message to the target destination
        """
        if self.enabled:
            if not self.checkTarget():
                return

            try:
                self.loggerClient.log(log)
            except:
                print 'Failed to log in %s' % self
                self.connected = False

