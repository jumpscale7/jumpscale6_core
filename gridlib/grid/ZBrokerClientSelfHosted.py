from OpenWizzy import o
import ujson
from ZBrokerClient import ZBrokerClient

#creates local connection when inside broker
class ZBrokerClientSelfHosted(ZBrokerClient):
    def __init__(self,broker):
        self.broker=broker

    def ping(self):
        return self.sendcmd("ping")

    def sendMsgOverCMDChannel(self,data):
        data=data[1:]
        return self.broker.processRPC(data)

    def sendcmd(self, cmd, **args):
        data = "4%s"%ujson.dumps([cmd, args])
        result = self.sendMsgOverCMDChannel(data)
        if result["state"] == "ok":
            return result["result"]
        else:
            raise RuntimeError("error in send cmd (error on server):%s, %s"%(cmd, result["result"]))        
