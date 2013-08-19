from OpenWizzy import o

import OpenWizzy.grid.serverbase
DaemonClienClass=o.servers.base.getDaemonClientClass()



try:
    import requests
except:
    o.system.installtools.execute("easy_install requests")
    import requests

class TornadoClient(DaemonClienClass):
    def __init__(self,addr="localhost",port=9999,org="myorg",user="root",passwd="passwd",ssl=False,roles=[]):

        self.timeout=60
        self.url="http://%s:%s/rpc/"%(addr,port)
        self.init(org=org,user=user,passwd=passwd,ssl=ssl,roles=roles,defaultSerialization="m")


    def _connect(self):
        """
        everwrite this method in implementation to init your connection to server (the transport layer)
        """
        pass

    def _close(self):
        """
        close the connection (reset all required)
        """
        pass


    def _sendMsg(self, cmd,data,sendformat="",returnformat=""):
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
        # headers={'Content-Type': 'application/octet-stream'}

        data2=o.servers.base._serializeBinSend(cmd,data,sendformat,returnformat,10)

        r = requests.post(self.url, data=data2, headers=headers)

        # r.status_code
        # r.headers['content-type']
        # r.encoding
        # r.text

        return o.servers.base._unserializeBinReturn(r.content)

        


