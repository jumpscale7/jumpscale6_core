from JumpScale.core.enumerators import AppStatusType
from JumpScale import j
from fb303_scripts import *
from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol 
import socket

class LogTargetScribe(object):
    
    """Forwards incoming logRecords to Scribe Server on localhost"""
    def __init__(self, serverip="localhost", serverport=9991):
        self._serverip = serverip
        self._server_real_ip = socket.gethostbyname(self._serverip)
        self._serverport = serverport
        self._client = None
        self._transport = None
        self.enabled = False
        self.checkTarget()
        self.name = "scribe"
        
    def checkTarget(self):
        """
        check status of scribe, if accessible return True
        """
        try:    
            result = j.cmdtools.logclient.getStatus()
        except AttributeError:
            result = AppStatusType.HALTED
            
        self.enabled = (result == AppStatusType.RUNNING) and self.open()
        return self.enabled

    def log(self, log):
        """
        forward the already formatted message to the target destination
        
        """
        message = message.replace('/|', '@@')
        try:
            type, _, _, level, _, _ = message.split('|')
        except:
            return True#invalid message, can't extract type and level
        category = "%s-%s"%(type, level)        
        log_entry = scribe.LogEntry(dict(category = category, message = message))
        if self._client==None:
            return False
        try:
            self._client.Log(messages=[log_entry])
        except:
            self.enabled = False
            self.close()
            return False
        return True
        
   
   
    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, LogTargetScribe):
            return False
        
        return (self._server_real_ip == other._server_real_ip) and (self._serverport == other._serverport)
    
    def __str__(self):
        """ string representation of a LogTargetScribe """
        return 'LogTargetScribe logging to %s:%d' % (str(self._serverip),self._serverport)

    __repr__ = __str__


    def open(self):
        """
        UDP has no notion of open, we are just preparing the thrift transport
        """
        try:
            if not self._transport:
                socket = TSocket.TSocket(host=self._serverip, port=self._serverport)
                self._transport = TTransport.TFramedTransport(socket)
                protocol = TBinaryProtocol.TBinaryProtocol(trans=self._transport, strictRead=False, strictWrite=False)
                self._client = scribe.Client(iprot=protocol, oprot=protocol)
            if not self._transport.isOpen():
                self._transport.open()
            return True
        except NameError:
            raise
        except Exception, ex:            
            return False            

        
    def close(self):
        if self._transport:
            self._transport.close()
