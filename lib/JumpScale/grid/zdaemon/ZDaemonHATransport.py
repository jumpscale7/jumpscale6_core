from JumpScale import j
import JumpScale.baselib.serializers
import JumpScale.grid.serverbase
from JumpScale.grid.serverbase.DaemonClient import Transport
from JumpScale.grid.zdaemon.ZDaemonTransport import ZDaemonTransport
import time

def retry(func):
    def wrapper(self, *args, **kwargs):
        try:
            if j.system.net.tcpPortConnectionTest(*self._connection[:2]):
                clientfunc = getattr(self._client, func.__name__)
                return clientfunc(*args, **kwargs)
        except:
            pass # we will execute the reconnect
        self._connection[2] = time.time()
        self.connect(self._id)
        clientfunc = getattr(self._client, func.__name__)
        return clientfunc(*args, **kwargs)
    return wrapper

class ZDaemonHATransport(Transport):
    def __init__(self, connections, gevent=False):
        self._connections = [ [ip, port, 0] for ip, port in connections ]
        self._timeout = 60
        self._gevent = gevent
        self._client = None
        self._id = None

    def connect(self, sessionid):
        if self._client:
            self._client.close()
        for attempt in xrange(2):
            for connection in sorted(self._connections, key=lambda c: c[2]):
                try:
                    if j.system.net.tcpPortConnectionTest(*connection[:2]):
                        self._id = sessionid
                        ip, port, timestamp = connection
                        client = ZDaemonTransport(ip, port, self._gevent)
                        client.connect(sessionid)
                        self._connection = connection
                        self._client = client
                        return
                except Exception:
                    pass # invalidate the client
                if self._client:
                    self._client.close()
                connection[2] = time.time()
        raise RuntimeError("Failed to connect to connections %s" % self._connections)

    @retry
    def sendMsg(self, category, cmd, data, sendformat="", returnformat="",timeout=None):
        pass

    def close(self):
        if self._client:
            self._client.close()
