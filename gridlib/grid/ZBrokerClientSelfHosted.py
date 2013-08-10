from OpenWizzy import o
# import OpenWizzy.baselib.serializers
# ujson = o.db.serializers.getSerializerType('j')
from .ZBrokerClient import ZBrokerClient
import sys
#creates local connection when inside broker
class ZBrokerClientSelfHosted(ZBrokerClient):
    def __init__(self,broker):
        self.broker=broker
        self.key=None

    def ping(self):
        return self.sendcmd("ping")

    def sendMsgOverCMDChannelFast(self,cmd,data,sendformat="m",returnformat="m"):
        # if sendformat<>"":
        #     ser=o.db.serializers.get(sendformat,key=self.key)
        #     data=ser.dumps(data)
        
        cmds=self.broker.cmdsInterfaces[0]
        result=eval("cmds.%s(**data)"%cmd)
        # try:
            
        # except Exception,e:            
        #     print "DEBUG NOW bug in sendMsgOverCMDChannelFast for ZBrokerClientSelfHosted"
        #     print "cmd was:%s"%cmd
        #     print "data was:%s"%data
        #     print e
        #     print sys.exit()            
                
        return result
