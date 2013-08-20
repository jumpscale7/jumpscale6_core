from OpenWizzy import o
import struct

import tornado.ioloop
import tornado.web
import OpenWizzy.grid.serverbase
import time



class JobHandler():
    def __init__(self):
        self.work={}

    def wait(self,org,user):
        print "wait:%s"%user
        key="%s_%s"%(org,user)
        while not self.work.has_key(key):
            time.sleep(1)
        return self.work[key]

    def scheduleJob(self,org,user,job):
        key="%s_%s"%(org,user)
        self.work[key]=1

class MainHandlerRPC(tornado.web.RequestHandler):
    """
    processes the incoming web requests
    """
    def initialize(self, server):
        self.server = server

    def post(self):
        data=self.request.body
        category,cmd,data2,informat,returnformat,sessionid=o.servers.base._unserializeBinSend(data)
        resultcode,returnformat,result=self.server.daemon.processRPCUnSerialized(cmd, informat, returnformat, data2, sessionid, category=category)
        data3=o.servers.base._serializeBinReturn(resultcode,returnformat,result)
        # resultcode,returnformat,result2=o.servers.base._unserializeBinReturn(data3)
        # if result<>result2:
        #     from IPython import embed
        #     print "DEBUG NOW serialization not work in post"
        #     embed()
        self.write(data3)
        # self.set_header('Content-Type','application/octet-stream')
        self.flush()

class MainHandlerGetWork(tornado.web.RequestHandler):
    """
    processes the incoming web requests
    """
    def initialize(self, server):
        self.server = server

    @tornado.web.asynchronous
    def get(self):
        print 'Request via GET', self
        from IPython import embed
        print "DEBUG NOW get"
        embed()        

    def wait(self,nrsec):
        self.server.ioloop.add_timeout(self.server.ioloop.time()+10,self.done)


    def done(self):
        self.write("YES WORKED")       
        self.finish()        

    
class TornadoServer():
    def __init__(self,addr,port,sslorg=None,ssluser=None,sslkeyvaluestor=None):
        """
        @param handler is passed as a class
        """
        self.port=port
        self.addr=addr
        self.key="1234"
        self.nr=0
        self.jobhandler=JobHandler()
        self.daemon=o.servers.base.getDaemon(sslorg=sslorg,ssluser=ssluser,sslkeyvaluestor=sslkeyvaluestor)
        self.application = tornado.web.Application([(r"/getwork/", MainHandlerGetWork,dict(server=self)),])
        self.application = tornado.web.Application([(r"/rpc/", MainHandlerRPC,dict(server=self)),])
        self.type="tornado"

    def start(self):
        print "started on %s" % self.port
        self.application.listen(self.port)
        self.ioloop=tornado.ioloop.IOLoop.instance()
        self.ioloop.start()

    def addCMDsInterface(self,MyCommands,category=""):
        self.daemon.addCMDsInterface(MyCommands,category)

