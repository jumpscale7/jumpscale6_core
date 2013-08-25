from JumpScale import j


import time


class ZDaemonFactory():

    def getZDaemon(self, port=4444, name="", nrCmdGreenlets=50, sslorg="", ssluser="", sslkeyvaluestor=None):
        """

        is a generic usable zmq daemon which has a data & cmd channel (data channel not completely implemented for now)


        zd=j.core.zdaemon.getZDaemon(port=5555,nrCmdGreenlets=50)

        class MyCommands():
            def __init__(self,daemon):
                self.daemon=daemon

                    def pingcmd(self,session=None):
                        return "pong"

                    def echo(self,msg="",session=None):
                        return msg

        #remark always need to add **args in method because user & returnformat are passed as params which can be used in method

        zd.setCMDsInterface(MyCommands)  #pass as class not as object !!!
        zd.start()

        use self.getZDaemonClientClass as client to this daemon

        """
        from ZDaemon import ZDaemon
        zd = ZDaemon(port=port, name=name, nrCmdGreenlets=nrCmdGreenlets, sslorg=sslorg, ssluser=ssluser, sslkeyvaluestor=sslkeyvaluestor)
        return zd

    def getZDaemonCMDS(self):
        return ZDaemonCMDS

    def getZDaemonClient(self, ipaddr="127.0.0.1", port=5555, org="myorg", user="root", passwd="1234", ssl=False, reset=False):
        """
        example usage, see example for server at self.getZDaemon

        client=j.core.zdaemon.getZDaemonClient(ipaddr="127.0.0.1",port=5555,login="root",passwd="1234",ssl=False)

                print client.echo("Hello World.")

        """
        from ZDaemonClient import ZDaemonClient
        cl = ZDaemonClient(ipaddr=ipaddr, port=port, org=org, user=user, passwd=passwd, ssl=ssl, reset=reset)
        return cl

    def getZDaemonAgent(self, ipaddr="127.0.0.1", port=5555, org="myorg", user="root", passwd="1234", ssl=False, reset=False, roles=[]):
        """
        example usage, see example for server at self.getZDaemon

        agent=j.core.zdaemon.getZDaemonAgent(ipaddr="127.0.0.1",port=5555,login="root",passwd="1234",ssl=False,roles=["*"])
        agent.start()

        @param roles describes which roles the agent can execute e.g. node.1,hypervisor.virtualbox.1,*
            * means all

        """
        from ZDaemonAgent import ZDaemonAgent
        cl = ZDaemonAgent(ipaddr=ipaddr, port=port, org=org, user=user, passwd=passwd, ssl=ssl, reset=reset, roles=roles)

        return cl

    def getZDaemonClientClass(self):
        """
        example usage, see example for server at self.getZDaemon
        when using as class can add methods to the client to make e.g. usage easier for consumer

        ZDaemonClientClass=j.core.zdaemon.getZDaemonClientClass()

        myClient(ZDaemonClientClass):
            def __init__(self,ipaddr="127.0.0.1",port=5555,org="myorg",user="root",passwd="1234",ssl=False,reset=False):
                ZDaemonClientClass.__init__(self,ipaddr=ipaddr,port=port,user=user,passwd=passwd,ssl=ssl,reset=reset)

        client=myClient()
        print client.echo("atest")

        """
        from ZDaemonClient import ZDaemonClient
        return ZDaemonClient

    def initSSL4Server(self, organization, serveruser, sslkeyvaluestor=None):
        """
        use this to init your ssl keys for the server (they can be used over all transports)
        """
        import JumpScale.grid.serverbase
        j.servers.base.initSSL4Server(organization, serveruser, sslkeyvaluestor)
