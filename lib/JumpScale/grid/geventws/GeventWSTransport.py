from JumpScale import j
import time
import JumpScale.grid.serverbase
from JumpScale.grid.serverbase.DaemonClient import Transport


import requests

class GeventWSTransport(Transport):
    def __init__(self, addr="localhost", port=9999):

        self.timeout = 60
        self.url = "http://%s:%s/rpc/" % (addr, port)
        self._id = None

    def connect(self, sessionid=None):
        """
        everwrite this method in implementation to init your connection to server (the transport layer)
        """
        self._id = sessionid

    def close(self):
        """
        close the connection (reset all required)
        """
        pass

    def sendMsg(self, category, cmd, data, sendformat="", returnformat="",retry=False):
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

        headers = {'content-type': 'application/raw'}
        data2 = j.servers.base._serializeBinSend(category, cmd, data, sendformat, returnformat, self._id)
        if retry:
            r=None
            while r==None:
                try:
                    r = requests.post(self.url, data=data2, headers=headers,timeout=600)
                except Exception,e:
                    print "retry connection to %s"%self.url
                    time.sleep(5)
        else:
            r = requests.post(self.url, data=data2, headers=headers,timeout=600)

                    
        if r.ok==False:
            eco=j.errorconditionhandler.getErrorConditionObject(msg='error 500 from webserver', msgpub='', \
                category='tornado.transport')
            return 99,"m",j.db.serializers.msgpack.dumps(eco.__dict__)

        return j.servers.base._unserializeBinReturn(r.content)
