from pylabs.InitBase import *
q.application.appname = "server"
q.application.start()

q.qshellconfig.interactive=True


# import zmq
import random
import sys
import time
import gevent
import zmq.green as zmq
import ujson


from GeventLoop import GeventLoop

class ZDaemonCMDS():
    def __init__(self,daemon):
        self.daemon=daemon

    def getfreeport(self):
        return self.daemon.getfreeportAndSchedule("datachannelProcessor",self.daemon.loggerGreenlet)

    def log(self,log):
        #in future should use bulk upload feature, now 1 by 1
        print log["message"]

    def pingcmd(self):
        return "pong"

class ZDaemon(GeventLoop):

    def __init__(self):
        GeventLoop.__init__(self)
        self.cmds={}
        self.ports=[]       
        self.sockets={}

        self.cmdsInterfaces=[ZDaemonCMDS(self)]

        self.schedule("cmdGreenlet",self.cmdGreenlet)

        self.watchdog={} #active ports are in this list

        # self.schedule("watchdog",self.watchdogCheck)
        # self.schedule("watchdogReset",self.watchdogReset)
        
        self.start()

    def addCMDsInterface(self,cmdInterfaceClass):
        self.cmdsInterfaces.append(cmdInterfaceClass(self))

    def datachannelProcessor(self,port):
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        
        socket.bind("tcp://*:%s" % port)
        self.sockets[port]=socket

        self.ports.append(port)

        print "init data port:%s"%port
        while True:
            msg = socket.recv()
            self.watchdog[port]=True
            if msg=="WATCHDOG":
                continue
            self.processRPC(msg)

    def getfreeportAndSchedule(self,name,method,port=3333,**args):
        found=None
        for i  in range(5010,5300):
            if i not in self.ports:
                found=i
                break
        if found==None:
            raise RuntimeError("Could not find free port")

        self.schedule("port_%s"%found,method,port=found,**args)

        for i  in range(1000):
            if found in self.ports:
                return found
            gevent.sleep(0.01)
                

        q.errorconditionhandler.raiseOperationalCritical(msgpub="Cannot open port nr %s for client daemon."%found,\
            message="",category="grid.startup",die=False,tags="")
        return 0

    def watchdogCheck(self):
        #ports without activity are closed
        while True:
            gevent.sleep(100)
            for port in self.ports:
                if port not in self.watchdog:
                    self.resetPort(port)

    def resetPort(self,port):
        greenlet=self.greenlets["port_%s"%port]
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
            self.watchdog={} #reset watchdog table

    def processRPC(self,data):
        # print "process rpc:\n%s"%data
        cmd=ujson.loads(data) #list with item 0=cmd, item 1=args
        cmd2={}
        if self.cmds.has_key(cmd[0]):
            ffunction=self.cmds[cmd[0]]
        else:
            ffunction=None
            for cmdinterface in self.cmdsInterfaces:
                try:
                    ffunction=eval("cmdinterface.%s"%cmd[0])
                except RuntimeError,e:
                    cmd2["state"]="error"
                    cmd2["result"]="cannot find cmd %s on cmdsInterfaces."%cmd[0]
            if ffunction==None:
                return cmd2
            else:
                cmd2={}
            self.cmds[cmd[0]]=ffunction

        try:
            result=ffunction(**cmd[1])
        except Exception,e:
            cmd2["state"]="error"            
            cmd2["result"]=str(e)
            return cmd2

        cmd2["state"]="ok"
        cmd2["result"]=result
        return cmd2

    def cmdGreenlet(self,port=4444):
        context = zmq.Context()
        cmdsocket = context.socket(zmq.REP)

        if q.system.platformtype.isLinux():
            cmdsocket.bind ("ipc:///tmp/cmdchannel_ZDaemon")
            print "IPC"
        else:
            cmdsocket.bind ("tcp://*:%s" % 4444)        

        print "init cmd channel on port:%s"%port
        while True:
            data = cmdsocket.recv()

            if data =="ping":
                cmdsocket.send("pong")
                continue

            result=self.processRPC(data)
            cmdsocket.send(ujson.dumps(result))

    def start(self):
        print "start"
        while True:
            gevent.sleep(1)


cd=ZDaemon()
