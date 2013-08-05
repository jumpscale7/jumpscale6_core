from OpenWizzy import o
from ..zdaemon.ZDaemonClient import ZDaemonClient

class ZLoggerClient(ZDaemonClient):

    def __init__(self,ipaddr="localhost", port=4444):
        ZDaemonClient.__init__(self,ipaddr=ipaddr,port=port,datachannel=False,servername="logger")

    def logMessage(self, logmessage):
        if logmessage.find("\n")<>-1:
            o.errorconditionhandler.raiseBug(message="logmessage cannot have \\n inside, msg was %s"%logmessage,category="loghandler.logmessage")
        logmessage = "1%s"%logmessage
        self.sendMsgOverCMDChannel(logmessage)

    def logECO(self, eco):
        """
        log ErrorConditionObject
        """
        eco.type=str(eco.type)
        self.sendcmd("logeco", eco=eco.__dict__)

