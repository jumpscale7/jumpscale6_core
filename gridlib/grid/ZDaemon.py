from OpenWizzy import o
import OpenWizzy.grid
# import zmq
import gevent
import gevent.monkey
import zmq.green as zmq
import time
from GeventLoop import GeventLoop
from gevent import queue as queue
import OpenWizzy.baselib.serializers

class ZDaemonCMDS():
    def __init__(self, daemon):
        self.daemon = daemon

    def getfreeport(self):
        """
        init a datachannelProcessor on found port
        is a server in pair socket processing incoming data
        each scheduled instance is on separate port
        """
        return self.daemon.getfreeportAndSchedule("datachannelProcessor", self.daemon.datachannelProcessor)

    def logeco(self, eco):
        eco["epoch"]=self.daemon.now
        eco=o.errorconditionhandler.getErrorConditionObject(ddict=eco)
        self.daemon.eventhandlingTE.executeV2(eco=eco,history=self.daemon.eventsMemLog)

    def pingcmd(self):
        return "pong"

class Dummy():
    pass

class ZDaemon(GeventLoop):

    def __init__(self, port=4444,name="",nrCmdGreenlets=50):
        gevent.monkey.patch_socket()
        
        GeventLoop.__init__(self)
        self.name=name        
        self.cmds = {}

        self.ports = [] #is for datachannel
        self.sockets = {} #is for datachannel

        self.cmdsInterfaces = [ZDaemonCMDS(self)]

        self.watchdog = {}  # active ports are in this list

        self.port=port

        self.now=0

        self.nrCmdGreenlets=nrCmdGreenlets


    def addCMDsInterface(self, cmdInterfaceClass):
        self.cmdsInterfaces.append(cmdInterfaceClass(self))

    def processRPC(self, data):
        # print "process rpc:\n%s"%data
        cmd = o.db.serializers.ujson.loads(data)  # list with item 0=cmd, item 1=args            
        cmd2 = {}
        if cmd[0] in self.cmds:
            ffunction = self.cmds[cmd[0]]
        else:
            ffunction = None

            for cmdinterface in self.cmdsInterfaces:
                if hasattr(cmdinterface,cmd[0]):
                    ffunction = getattr(cmdinterface, cmd[0])

            if ffunction == None:
                cmd2["state"] = "nomethod"
                cmd2["result"] = "cannot find cmd %s on cmdsInterfaces."%cmd[0]
                return cmd2
            else:
                cmd2 = {}
            self.cmds[cmd[0]] = ffunction        

        try:
            result = ffunction(**cmd[1])
        except Exception, e:
            eco=o.errorconditionhandler.parsePythonErrorObject(e)
            eco.level=2
            cmd2["state"] = "error"
            cmd2["result"] = eco
            # print eco
            o.errorconditionhandler.processErrorConditionObject(eco)
            return cmd2

        cmd2["state"] = "ok"
        cmd2["result"] = result
        return cmd2

    def repCmdServer(self):
        cmdsocket = self.cmdcontext.socket(zmq.REP)
        cmdsocket.connect("inproc://cmdworkers")
        while True:
            data = cmdsocket.recv()

            if data[0] == "1":
                self.logQueue.put(data[1:])
                cmdsocket.send("OK")
            elif data[0] == "3":
                data = data[1:]
                result = self.processRPC(data)
                if result["state"]=="ok":
                    cmdsocket.send(result["result"])
                else:
                    cmdsocket.send("ERROR:%s"%o.db.serializers.ujson.dumps(result))
            elif data[0] == "4":
                data = data[1:]
                result = self.processRPC(data)
                cmdsocket.send(o.db.serializers.ujson.dumps(result))
            else:
                q.errorconditionhandler.raiseBug(message="Could not find supported message on cmd server",category="grid.cmdserver.valueerror")


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
                message = frontend.recv()
                more = frontend.getsockopt(zmq.RCVMORE)
                if more:
                    backend.send(message, zmq.SNDMORE)
                else:
                    backend.send(message)

            if socks.get(backend) == zmq.POLLIN:
                message = backend.recv()
                more = backend.getsockopt(zmq.RCVMORE)
                if more:
                    frontend.send(message, zmq.SNDMORE)
                else:
                    frontend.send(message)


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
