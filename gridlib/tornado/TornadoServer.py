from OpenWizzy import o
import struct

import tornado.ioloop
import tornado.web
import OpenWizzy.grid.serverbase

class MainHandler(tornado.web.RequestHandler):
    """
    processes the incoming web requests
    """
    def initialize(self, server):
        self.server = server

    def get(self):
        self.write("Hello, world")


    
class TornadoServer():
    def __init__(self,addr,port,sslorg=None,ssluser=None,sslkeyvaluestor=None):
        """
        @param handler is passed as a class
        """
        self.port=port
        self.addr=addr
        self.key="1234"
        self.daemon=o.servers.base.getDaemon(sslorg=sslorg,ssluser=ssluser,sslkeyvaluestor=sslkeyvaluestor)
        self.application = tornado.web.Application([(r"/", MainHandler,dict(server=self)),])
        self.type="tornado"

    def start(self):
        print "started on %s" % self.port
        self.application.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

    def addCMDsInterface(self,MyCommands,category="optional"):
        self.daemon.addCMDsInterface(MyCommands,category)


class TornadoServerFactory():

    def get(self,port,sslorg=None,ssluser=None,sslkeyvaluestor=None):
        """        
        HOW TO USE:
        daemon=o.servers.tornado.get(port=4444)

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
        return TornadoServer('',port)

    def getClient(self,addr,port,key):
        return SocketServerClient(addr,port,key)



