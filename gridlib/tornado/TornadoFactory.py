from OpenWizzy import o


class TornadoFactory():

    def getServer(self,port,sslorg=None,ssluser=None,sslkeyvaluestor=None):
        """        
        HOW TO USE:
        daemon=o.servers.tornado.getServer(port=4444)

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
        from .TornadoServer import TornadoServer
        return TornadoServer('',port)

    def getClient(self,addr,port,category="core",org="myorg",user="root",passwd="passwd",ssl=False,roles=[]):
        from .TornadoClient import TornadoClient
        return TornadoClient(addr=addr,port=port,category=category,org=org,user=user,passwd=passwd,ssl=ssl,roles=roles)

    def initSSL4Server(self,organization,serveruser,sslkeyvaluestor=None):
        """
        use this to init your ssl keys for the server (they can be used over all transports)
        """
        import OpenWizzy.grid.serverbase
        o.servers.base.initSSL4Server(organization,serveruser,sslkeyvaluestor)        


