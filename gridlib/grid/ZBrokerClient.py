from OpenWizzy import o

from ..zdaemon.ZDaemonClient import ZDaemonClient

class ZBrokerClient(ZDaemonClient):
    def __init__(self,ipaddr="localhost",port=5554):
        ZDaemonClient.__init__(self,ipaddr=ipaddr,port=port,servername="broker")
        self._init()

    def _init(self):        
        pass

    def ping(self):
        return self.sendcmd("ping")

    def registerNode(self,obj):
        return self.sendcmd("registerNode",obj=obj.__dict__)

    def registerProcess(self,obj):
        return self.sendcmd("registerProcess",obj=obj.__dict__)

    def registerApplication(self,name,description="",pid=0):
        return self.sendcmd("registerApplication",name=name,description=description,pid=pid)

    def list(self,namespace,category,prefix=""):
        namespaceid,catid=self._getIds(namespace,category)
        return self.sendcmd("list",namespaceid=namespaceid,catid=catid,prefix=prefix)

