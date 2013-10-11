import socket
#from JumpScale.core.logging.LogConsoleServer import ManagementProtocol


DEFAULT_PORT = 9998
class LogTargetToJumpScaleLogConsole(object):
    """Forwards incoming logRecords to TCP-server"""
    def __init__(self, serverip="localhost", serverport=DEFAULT_PORT):
        self.connected = False
        self._serverip = serverip
        self._server_real_ip = socket.gethostbyname(self._serverip)
        self._serverport = serverport
        self.enabled = self.checkTarget()
        self.name="console"
        self.enabled = False

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        result=self.open()
        if result==False:
            self.close()            
        return result


    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, LogTargetToJumpScaleLogConsole):
            return False

        return (self._server_real_ip == other._server_real_ip) and (self._serverport == other._serverport)

    def __str__(self):
        """ string representation of a LogTargetServer """
        return 'LogTargetToJumpScaleLogConsole logging to %s:%d' % (str(self._serverip), self._serverport)

    __repr__ = __str__


    def close(self):
        try:
            self._sock.close()
        except:
            pass
        self.connected = False
        self.enabled=False


    def open(self):
        if self.connected:
            return True
        try:
            #self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self._sock.connect((self._server_real_ip, self._serverport))
            self._sock=socket.create_connection((self._server_real_ip, self._serverport),timeout=1)
            self.connected = True
            self.enabled = True
        except socket.error, ex:
            self.close()
        return self.connected

    def log(self, log):
        """
        forward the already formatted message to the target destination

        """
        logged = False
        if not self.connected:
            #raise RuntimeError("log() called on a disabled logtarget %s"%self.__class__)
            return False
        try:
            self._sock.sendall(str(message) + ManagementProtocol.MSG_TERMINATOR)
            logged = True
        except socket.error, ex:
            self.close()
            self.enabled =  False
            #one message lost

        return logged
