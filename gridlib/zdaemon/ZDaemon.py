from OpenWizzy import o
# import OpenWizzy.grid
# import zmq
import gevent
import gevent.monkey
import zmq.green as zmq
import time
from gevent import queue as queue
import OpenWizzy.baselib.serializers
import inspect

GeventLoop=o.core.gevent.getGeventLoopClass()

class ZDaemon(GeventLoop):

    def __init__(self, port=4444,name="",nrCmdGreenlets=50):
        gevent.monkey.patch_socket()
        GeventLoop.__init__(self)

        self.name=name
        self.cmds = {}

        self.ports = [] #is for datachannel
        self.sockets = {} #is for datachannel

        self.cmdsInterfaces = []

        self.watchdog = {}  # active ports are in this list

        self.port=port

        self.now=0

        self.nrCmdGreenlets=nrCmdGreenlets

        self.sessions={}

        self.key=""

    def addCMDsInterface(self, cmdInterfaceClass):
        self.cmdsInterfaces.append(cmdInterfaceClass(self))

    def setCMDsInterface(self, cmdInterfaceClass):
        self.cmdsInterfaces=[]
        self.cmdsInterfaces.append(cmdInterfaceClass(self))

    def processRPC(self, cmd,data,returnformat,session):
        """
        list with item 0=cmd, item 1=args (dict)

        @return (resultcode,result)
        resultcode
            0=ok
            1= not authenticated
            2= method not found
            2+ any other error
        """
        # print "process rpc:\n%s"%data
        cmd2 = {}
        if cmd in self.cmds:
            ffunction = self.cmds[cmd]
        else:
            ffunction = None

            for cmdinterface in self.cmdsInterfaces:
                if hasattr(cmdinterface,cmd):
                    ffunction = getattr(cmdinterface, cmd)

            if ffunction == None:
                #means could not find method
                return "2","",None
            else:
                cmd2 = {}
            self.cmds[cmd] = ffunction

        try:
            args = inspect.getargspec(ffunction)
            if 'session' in args.args and isinstance(data, dict):
                data['session'] = session
            if isinstance(data, dict):
                result = ffunction(**data)
            else:
                result = ffunction(data)
        except Exception, e:
            eco=o.errorconditionhandler.parsePythonErrorObject(e)
            eco.level=2
            print eco
            o.errorconditionhandler.processErrorConditionObject(eco)
            s=o.db.serializers.getSerializerType("m")
            return "3","",s.dumps(eco.__dict__)

        return "0",returnformat,result


    def repCmdServer(self):
        cmdsocket = self.cmdcontext.socket(zmq.REP)
        cmdsocket.connect("inproc://cmdworkers")
        while True:
            cmd,informat,returnformat,data,sessionid = cmdsocket.recv_multipart()


            # if data[0] == "1":
            #     self.logQueue.put(data[1:])
            #     cmdsocket.send("OK")

            if self.sessions.has_key(sessionid):
                session=self.sessions[sessionid]
            else:
                if cmd in ["registerpubkey","getpubkeyserver","registersession"]:
                    session=None
                    returnformat=""
                else:
                    ser = o.db.serializers.get("m")
                    error = "Authentication  or Session error, session not known with id:%s"%sessionid
                    eco = o.errorconditionhandler.getErrorConditionObject(msg=error)
                    cmdsocket.send_multipart(("3","", ser.dumps(eco.__dict__)))
                    continue

            if informat<>"":
                ser=o.db.serializers.get(informat,key=self.key)
                data=ser.loads(data)                
            parts = self.processRPC(cmd,data,returnformat=returnformat,session=session)
            returnformat=parts[1] #return format as comes back from processRPC
            if returnformat<>"": #is 
                returnser = o.db.serializers.get(returnformat,key=session.encrkey)
                data=returnser.dumps(parts[2])
            else:
                data=parts[2]

            if data==None:
                data=""
            cmdsocket.send_multipart((parts[0],parts[1],data))

    def cmdGreenlet(self):
        #Nonblocking, e.g the osis server contains a broker which queus internally the messages.
        self.cmdcontext = zmq.Context()


        frontend = self.cmdcontext.socket(zmq.ROUTER)
        backend = self.cmdcontext.socket(zmq.DEALER)

        frontend.bind("tcp://*:%s" % self.port)
        backend.bind("inproc://cmdworkers")

        # Initialize poll set
        poller = zmq.Poller()
        poller.register(frontend, zmq.POLLIN)
        poller.register(backend, zmq.POLLIN)

        workers = []

        for i in range(self.nrCmdGreenlets):
            workers.append(gevent.spawn(self.repCmdServer))


        o.logger.log("init cmd channel on port:%s for daemon:%s"%(self.port,self.name), level=5, category="zdaemon.init") 


        while True:
            socks = dict(poller.poll())
            if socks.get(frontend) == zmq.POLLIN:
                parts=frontend.recv_multipart()
                parts.append(parts[0]) #add session id at end
                backend.send_multipart([parts[0]]+parts)

            if socks.get(backend) == zmq.POLLIN:
                parts = backend.recv_multipart()
                frontend.send_multipart( parts[1:]) #@todo dont understand why I need to remove first part of parts?


    def start(self,mainloop=None):
        self.schedule("cmdGreenlet", self.cmdGreenlet)
        self.startClock()

        print "start"
        if mainloop<>None:
            mainloop()
        else:
            while True:
                gevent.sleep(100)

    ##UNFINISHED CODE FOR DATACHANNEL (still duplicate code inside) ################################

    def datachannelStart(self):
        self.schedule("returok", self.datachannelReturnok)
        self.schedule("watchdog",self.watchdogCheck)
        self.schedule("watchdogReset",self.watchdogReset)


    def datachannelProcessor(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)

        socket.bind("tcp://*:%s" % port)
        self.sockets[port] = socket

        self.ports.append(port)

        print "init data port:%s"%port
        while True:
            msg = socket.recv()
            self.watchdog[port] = True
            if msg == "WATCHDOG":
                continue
            self.processRPC(msg)

    def datachannelReturnok(self):
        """
        will every 5 sec go back to sender to acknowledge succesfull processed items
        """
        while True:
            self.socket.send(str(self.counter))
            #print "send"
            gevent.sleep(5)

    def getfreeportAndSchedule(self, name, method, **args):
        """
        find a free port & attach method to it

        """
        found = None
        for i in range(5010, 5300):
            if i not in self.ports:
                found = i
                break
        if found == None:
            raise RuntimeError("Could not find free port")

        self.schedule("port_%s"%found, method, port=found, **args)

        for i in range(1000):
            if found in self.ports:
                return found
            gevent.sleep(0.01)

        o.errorconditionhandler.raiseOperationalCritical(msgpub="Cannot open port nr %s for client daemon."%found,
                                                         message="", category="grid.startup", die=False, tags="")
        return 0

    def watchdogCheck(self):
        # ports without activity are closed
        while True:
            gevent.sleep(100)
            for port in self.ports:
                if port not in self.watchdog:
                    self.resetPort(port)

    def resetPort(self, port):
        greenlet = self.greenlets["port_%s"%port]
        greenlet.kill()
        self.sockets[port].setsockopt(zmq.LINGER, 0)
        self.sockets[port].close()
        print "Killed socket %s"%port
        try:
            self.watchdog.pop(port)
        except:
            pass
        try:
            self.ports.remove(port)
        except:
            pass

    def watchdogReset(self):
        while True:
            gevent.sleep(10)
            self.watchdog = {}  # reset watchdog table


    ###############################################################
