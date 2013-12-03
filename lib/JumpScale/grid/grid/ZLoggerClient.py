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
        
        if j.basetype.dictionary.check(logobject):
            args = {}
            args["log"] = logobject
        else:
            args = {}
            args["log"] = logobject.__dict__

        # print args["log"] 

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

    def logbatch(self, logs):
        args = dict()
        batch = list()
        for log in logs:
            if not isinstance(log, dict):
                log = log.__dict__
            batch.append(log)
        args['logbatch'] = batch
        self.client.sendMsgOverCMDChannel("logbatch", data=args, sendformat="m", returnformat="", category="logger")
