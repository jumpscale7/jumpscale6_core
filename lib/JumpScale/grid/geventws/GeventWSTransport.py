from JumpScale import j
import time
import JumpScale.grid.serverbase
from JumpScale.grid.serverbase.DaemonClient import Transport


import grequests as requests

class GeventWSTransport(Transport):
    def __init__(self, addr="localhost", port=9999):

        self.url = "http://%s:%s/rpc/" % (addr, port)
        self._id = None
        self._addr = addr
        self._port = port

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

    def sendMsg(self, category, cmd, data, sendformat="", returnformat="",retry=True,timeout=60):
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
        start=j.base.time.getTimeEpoch()
        if self.timeout:
            timeout = self.timeout
        if retry:
            r=None
            while r==None:
                now=j.base.time.getTimeEpoch()
                if now>start+timeout:
                    break
                try:
                    r = requests.post(self.url, data=data2, headers=headers,timeout=timeout)
                    responses=requests.map([r])
                    rcv=responses[0]
                    # rcv = r.send()
                except Exception,e:
                    if str(e).find("Connection refused")<>-1:
                        print "retry connection to %s"%self.url
                        time.sleep(0.1)
                    else:
                        from IPython import embed
                        print "DEBUG NOW error in GeventWSTransport"
                        embed()
                        
                        raise RuntimeError("error to send msg to %s,error was %s"%(self.url,e))

        else:
            print "NO RETRY ON REQUEST WS TRANSPORT"
            r = requests.post(self.url, data=data2, headers=headers,timeout=timeout)

        # rcv = r.send()

        if rcv==None:
            eco=j.errorconditionhandler.getErrorConditionObject(msg='timeout on request to %s'%self.url, msgpub='', \
                category='gevent.transport')
            return "4","m",j.db.serializers.msgpack.dumps(eco.__dict__)
                    
        if rcv.ok==False:
            eco=j.errorconditionhandler.getErrorConditionObject(msg='error 500 from webserver on %s'%self.url, msgpub='', \
                category='gevent.transport')
            return "6","m",j.db.serializers.msgpack.dumps(eco.__dict__)

        return j.servers.base._unserializeBinReturn(rcv.content)
