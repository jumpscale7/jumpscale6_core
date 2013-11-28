from JumpScale import j


class GeventWSFactory():

    def getServer(self, port, sslorg=None, ssluser=None, sslkeyvaluestor=None):
        """
        HOW TO USE:
        daemon=j.servers.tornado.getServer(port=4444)

        class MyCommands():
            def __init__(self,daemon):
                self.daemon=daemon

            #session always needs to be there
            def pingcmd(self,session=session):
                return "pong"

            def echo(self,msg="",session=session):
                return msg

        daemon.addCMDsInterface(MyCommands,category="optional")  #pass as class not as object !!! chose category if only 1 then can leave ""

        daemon.start()

        """
        from .GeventWSServer import GeventWSServer
        return GeventWSServer('', port, ssluser=ssluser, sslorg=sslorg, sslkeyvaluestor=sslkeyvaluestor)

    def getClient(self, addr, port, category="core", org="myorg", user="root", passwd="passwd", ssl=False, roles=[],id=None,timeout=60):
        from .GeventWSTransport import GeventWSTransport
        from JumpScale.grid.serverbase.DaemonClient import DaemonClient
        trans = GeventWSTransport(addr, port)
        trans.timeout=timeout

        cl = DaemonClient(org=org, user=user, passwd=passwd, ssl=ssl, transport=trans,id=id)
        return cl.getCmdClient(category)

    def initSSL4Server(self, organization, serveruser, sslkeyvaluestor=None):
        """
        use this to init your ssl keys for the server (they can be used over all transports)
        """
        import JumpScale.grid.serverbase
        j.servers.base.initSSL4Server(organization, serveruser, sslkeyvaluestor)
