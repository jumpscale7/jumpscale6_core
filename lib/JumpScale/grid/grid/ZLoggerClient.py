from JumpScale import j
from ..zdaemon.ZDaemonTransport import ZDaemonTransport
from ..serverbase.DaemonClient import DaemonClient

class ZLoggerClient(object):

    def __init__(self, ipaddr="localhost", port=4443):
        trans = ZDaemonTransport(ipaddr, port)
        self.client = DaemonClient(org='org', user='root', passwd='1234', transport=trans)

    @j.logger.nologger
    def log(self, logobject):

        # logmessage = "1%s"%logmessage
        args = {}
        args["log"] = logobject.__dict__

        self.client.sendMsgOverCMDChannel("log", data=args, sendformat="m", returnformat="", category="logger")

    def logECO(self, eco):
        """
        log ErrorConditionObject
        """
        eco.type = str(eco.type)
        args = {}
        args["eco"] = eco.__dict__
        print "log eco:%s"%eco
        self.client.sendMsgOverCMDChannel("logeco", data=args, sendformat="m", returnformat="", category="logger")
