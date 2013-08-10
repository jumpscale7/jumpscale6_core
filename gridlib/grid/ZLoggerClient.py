from OpenWizzy import o
from ..zdaemon.ZDaemonClient import ZDaemonClient

class ZLoggerClient(ZDaemonClient):

    def __init__(self,ipaddr="localhost", port=4444):

        ZDaemonClient.__init__(self,ipaddr=ipaddr,port=port,datachannel=False,ssl=False)
            

    def log(self, logobject):

        # logmessage = "1%s"%logmessage
        args={}
        args["log"]=logobject.__dict__
        
        self.sendMsgOverCMDChannelFast("log",data=args,sendformat="m",returnformat="")

    def logECO(self, eco):
        """
        log ErrorConditionObject
        """
        eco.type=str(eco.type)
        args={}
        args["eco"]=eco.__dict__       
        self.sendMsgOverCMDChannelFast("logeco",data=args,sendformat="m",returnformat="")

