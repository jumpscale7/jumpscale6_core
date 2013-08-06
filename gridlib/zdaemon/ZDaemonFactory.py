from OpenWizzy import o

from ZDaemonCMDS import ZDaemonCMDS
from ZDaemon import ZDaemon
from ZDaemonClient import ZDaemonCmdClient
from ZDaemonAgent import ZDaemonAgent

import time

class ZDaemonFactory():

    def getZDaemon(self, port=4444,name="",nrCmdGreenlets=50,sslorg="",ssluser="",sslkeyvaluestor=None):
        """

        is a generic usable zmq daemon which has a data & cmd channel (data channel not completely implemented for now)


        zd=o.core.zdaemon.getZDaemon(port=5555,nrCmdGreenlets=50)

        ZDaemonCMDS=o.core.zdaemon.getZDaemonCMDS()  #get base class which needs to be used as basis for commands

        class MyCommands(ZDaemonCMDS):
            def __init__(self,daemon):
                self.daemon=daemon

		    def pingcmd(self,**args):
		        return "pong"

		    def echo(self,msg="",**args):
		        return msg

        #remark always need to add **args in method because user & returnformat are passed as params which can be used in method

        zd.setCMDsInterface(MyCommands)  #pass as class not as object !!!
        zd.start()

        use self.getZDaemonClientClass as client to this daemon

        """

        zd=ZDaemon(port=port,name=name,nrCmdGreenlets=nrCmdGreenlets)
        if ssluser<>"":
            from OpenWizzy.baselib.ssl.SSL import SSL
            zd.ssluser=ssluser
            zd.sslorg=sslorg
            zd.keystor=SSL().getSSLHandler(sslkeyvaluestor)            
        else:
            zd.keystor=None
            zd.ssluser=None
            zd.sslorg=None
        return zd

    def getZDaemonCMDS(self):
    	return ZDaemonCMDS

    def getZDaemonClient(self,ipaddr="127.0.0.1",port=5555,org="myorg",user="root",passwd="1234",ssl=False,reset=False):
        """
        example usage, see example for server at self.getZDaemon

        client=o.core.zdaemon.getZDaemonClient(ipaddr="127.0.0.1",port=5555,login="root",passwd="1234",ssl=False)

		print client.echo("Hello World.")

        """
        cl=ZDaemonCmdClient(ipaddr=ipaddr,port=port,org=org,user=user,passwd=passwd,ssl=ssl,reset=reset)

        return cl

    def getZDaemonAgent(self,ipaddr="127.0.0.1",port=5555,org="myorg",user="root",passwd="1234",ssl=False,reset=False,roles=[]):
        """
        example usage, see example for server at self.getZDaemon

        agent=o.core.zdaemon.getZDaemonAgent(ipaddr="127.0.0.1",port=5555,login="root",passwd="1234",ssl=False,roles=["*"])
        agent.start()

        @param roles describes which roles the agent can execute e.g. node.1,hypervisor.virtualbox.1,*  
            * means all

        """
        cl=ZDaemonAgent(ipaddr=ipaddr,port=port,org=org,user=user,passwd=passwd,ssl=ssl,reset=reset,roles=roles)

        return cl

    def getZDaemonClientClass(self):
        """
        example usage, see example for server at self.getZDaemon
        when using as class can add methods to the client to make e.g. usage easier for consumer

        ZDaemonClientClass=o.core.zdaemon.getZDaemonClientClass()

        myClient(ZDaemonClientClass):
            def __init__(self,ipaddr="127.0.0.1",port=5555,org="myorg",user="root",passwd="1234",ssl=False,reset=False):
                ZDaemonClientClass.__init__(self,ipaddr=ipaddr,port=port,user=user,passwd=passwd,ssl=ssl,reset=reset)

        client=myClient()
        print client.echo("atest")

        """
        return ZDaemonCmdClient        

    def initSSL4Server(self,organization,serveruser,sslkeyvaluestor=None):
        from OpenWizzy.baselib.ssl.SSL import SSL
        ks=SSL().getSSLHandler(sslkeyvaluestor)
        ks.createKeyPair(organization, serveruser)

