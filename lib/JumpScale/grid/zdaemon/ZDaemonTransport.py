from JumpScale import j
import JumpScale.baselib.serializers
import zmq
import JumpScale.grid.serverbase
from JumpScale.grid.serverbase.DaemonClient import Transport


class ZDaemonTransport(Transport):
    def __init__(self, addr="localhost", port=9999):

        self._timeout = 60
        self._addr = addr
        self._port = port
        self._id = None

    def connect(self, sessionid):
        """
        everwrite this method in implementation to init your connection to server (the transport layer)
        """
        self._id = sessionid
        self._init()

    def sendMsg(self, category, cmd, data, sendformat="", returnformat=""):
        """
        overwrite this class in implementation to send & retrieve info from the server (implement the transport layer)

        @return (resultcode,returnformat,result)
                item 0=cmd, item 1=returnformat (str), item 2=args (dict)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """

        self._cmdchannel.send_multipart([category, cmd, sendformat, returnformat, data])
        return self._cmdchannel.recv_multipart()

    def _init(self):
        j.logger.log("check server is reachable on %s on port %s" % (self._addr, self._port), level=4, category='zdaemon.client.init')
        res = j.system.net.waitConnectionTest(self._addr, self._port, 10)

        if res == False:
            msg = "Could not find a running server instance  on %s:%s" % (self._addr, self._port)
            raise RuntimeError("s")
            j.errorconditionhandler.raiseOperationalCritical(msgpub=msg, message="", category="zdaemonclient.init", die=True)
        j.logger.log("server is reachable on %s on port %s" % (self._addr, self._port), level=4, category='zdaemon.client.init')

        self._context = zmq.Context()

        self._cmdchannel = self._context.socket(zmq.REQ)

        self._cmdchannel.setsockopt(zmq.IDENTITY, self._id)

        # if self.port == 4444 and j.system.platformtype.isLinux():
        #     self.cmdchannel.connect("ipc:///tmp/cmdchannel_clientdaemon")
        #     print "IPC channel opened to client daemon"
        # else:
        self._cmdchannel.connect("tcp://%s:%s" % (self._addr, self._port))
        print "TCP channel opened to %s:%s" % (self._addr, self._port)

        self._poll = zmq.Poller()
        self._poll.register(self._cmdchannel, zmq.POLLIN)

    def close(self):
        try:
            self._cmdchannel.setsockopt(zmq.LINGER, 0)
            self._cmdchannel.close()
        except:
            print "error in close for cmdchannel"
            pass

        try:
            self._poll.unregister(self._cmdchannel)
        except:
            pass

        self._context.term()

