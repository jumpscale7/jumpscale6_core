from JumpScale import j
from gevent.pywsgi import WSGIServer
from gevent import monkey; monkey.patch_all()
import JumpScale.grid.serverbase


class GeventWSServer():

    def __init__(self, addr, port, sslorg=None, ssluser=None, sslkeyvaluestor=None):
        """
        @param handler is passed as a class
        """
        self.port = port
        self.addr = addr
        self.key = "1234"
        self.nr = 0
        # self.jobhandler = JobHandler()
        self.daemon = j.servers.base.getDaemon(sslorg=sslorg, ssluser=ssluser, sslkeyvaluestor=sslkeyvaluestor)
        self.application = WSGIServer(('', self.port), self.rpcRequest)
        self.type = "geventws"

    def responseRaw(self,data,start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [data]
    
    def responseNotFound(self,start_response):
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return ['<h1>Not Found</h1>']

    def rpcRequest(self, environ, start_response):
        if environ["CONTENT_TYPE"]=='application/raw' and environ["REQUEST_METHOD"]=='POST':
            data=environ["wsgi.input"].read()
            category, cmd, data2, informat, returnformat, sessionid = j.servers.base._unserializeBinSend(data)
            resultcode, returnformat, result = self.daemon.processRPCUnSerialized(cmd, informat, returnformat, data2, sessionid, category=category)
            data3 = j.servers.base._serializeBinReturn(resultcode, returnformat, result)
            return self.responseRaw(data3,start_response)
        else:
            return self.responseNotFound(start_response)

    # def router(self, environ, start_response):
    #     path = environ["PATH_INFO"].lstrip("/")
    #     if path == "" or path.rstrip("/") == "wiki":
    #         path == "wiki/system"
    #     print "path:%s" % path

    #     if path.find("favicon.ico") != -1:
    #         return self.processor_page(environ, start_response, self.filesroot, "favicon.ico", prefix="")

    #     ctx = RequestContext(application="", actor="", method="", env=environ,
    #                          start_response=start_response, path=path, params=None)
    #     ctx.params = self._getParamsFromEnv(environ, ctx)

    def start(self):
        print "started on %s" % self.port
        self.application.serve_forever()

    def addCMDsInterface(self, MyCommands, category=""):
        self.daemon.addCMDsInterface(MyCommands, category)
