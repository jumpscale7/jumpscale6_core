from OpenWizzy import o

from Daemon import Daemon
import time

class ServerBaseFactory():

    def getDaemon(self, name="unknown",sslorg="",ssluser="",sslkeyvaluestor=None):
        """

        is the basis for every daemon we create which can be exposed over e.g. zmq or sockets or http


        daemon=o.servers.base.getDaemon()

        class MyCommands():
            def __init__(self,daemon):
                self.daemon=daemon

            #session always needs to be there
		    def pingcmd(self,session=session):
		        return "pong"

		    def echo(self,msg="",session=session):
		        return msg

        daemon.setCMDsInterface(MyCommands,category="optional")  #pass as class not as object !!! chose category if only 1 then can leave ""

        #now you need to pass this to a protocol server, its not usable by itself

        """
        
        zd=Daemon(name=name)
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

    def initSSL4Server(self,organization,serveruser,sslkeyvaluestor=None):
        from OpenWizzy.baselib.ssl.SSL import SSL
        ks=SSL().getSSLHandler(sslkeyvaluestor)
        ks.createKeyPair(organization, serveruser)

