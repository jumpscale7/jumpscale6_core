from OpenWizzy import o
import zmq
import time
ujson = o.db.serializers.ujson


class ZDaemonClient():
    def __init__(self,ipaddr="localhost", port=4444,datachannel=False,servername=""):
        if servername=="":
            raise RuntimeError("servername cannot be empty")
            o.errorconditionhandler.raiseBug(message="servername cannot be empty",category="grid.init") #@todo URGENT: this does not show stacktrace well
        self.retry = True
        self.port=port
        self.ipaddr=ipaddr
        self.datachannel=datachannel
        self.servername=servername
        self.init()

    def init(self):

        o.logger.log("check if %s is reachable on %s on port %s" % (self.servername,self.ipaddr,self.port), level=4, category='zdaemon.client.init')
        res=o.system.net.waitConnectionTest(self.ipaddr,self.port,20)
        if res==False:
            msg="Could not find a running server instance with name %s on %s:%s"%(self.servername,self.ipaddr,self.port)
            o.errorconditionhandler.raiseOperationalCritical(msgpub=msg,message="",category="zdaemonclient.init",die=True)
        o.logger.log("%s is reachable on %s on port %s" % (self.servername,self.ipaddr,self.port), level=4, category='zdaemon.client.init')

        self.context = zmq.Context()

        self.cmdchannel = self.context.socket(zmq.REQ)

        # if self.port == 4444 and o.system.platformtype.ubuntu.checkIsUbuntu():
        #     self.cmdchannel.connect("ipc:///tmp/cmdchannel_clientdaemon")
        #     print "IPC channel opened to client daemon"
        # else:
        self.cmdchannel.connect("tcp://%s:%s" % (self.ipaddr,self.port))
        print "TCP channel opened to %s:%s:%s"%(self.servername,self.ipaddr,self.port)

        self.poll = zmq.Poller()
        self.poll.register(self.cmdchannel, zmq.POLLIN)

        if self.datachannel:
            port = int(self.sendcmd("getfreeport"))
            if port == 0:
                raise RuntimeError("Could not find free port on clientdaemon")

            self.datachannel = self.context.socket(zmq.PAIR)
            self.datachannel.connect("tcp://localhost:%s" % port)

            print "init port for datachannel: %s"%port

    def sendMsgOverCMDChannelFast(self, msg):
        self.cmdchannel.send(msg)
        return self.cmdchannel.recv()

    def sendMsgOverCMDChannel(self, msg):
        if self.retry:
            while True:
                # print "Send (%s)" % msg
                self.cmdchannel.send(msg)
                expect_reply = True
                while expect_reply:
                    socks = dict(self.poll.poll(1000))
                    if socks.get(self.cmdchannel) == zmq.POLLIN:
                        reply = self.cmdchannel.recv()
                        if not reply:
                            break
                        else:
                            return reply
                    else:
                        print "W: No response from clientdaemon, retrying"
                        self.reset()
                        self.cmdchannel.send(msg)
            return reply
        else:
            print "Send once (%s)" % msg
            self.cmdchannel.send(msg)
            socks = dict(self.poll.poll(1000))
            if socks.get(self.cmdchannel) == zmq.POLLIN:
                return self.cmdchannel.recv()
            else:
                o.errorconditionhandler.raiseOperationalCritical(message="", category="",
                                                                 msgpub="could not communicate with cmdclient daemon on port %s"%4444, die=True, tags="")

    def close(self):
        try:
            self.cmdchannel.setsockopt(zmq.LINGER, 0)
            self.cmdchannel.close()
        except:
            print "error in close for cmdchannel"
            pass

        try:
            self.poll.unregister(self.cmdchannel)
        except:
            pass

        try:
            self.datachannel.setsockopt(zmq.LINGER, 0)
            self.datachannel.close()
        except:
            # print "error in close for datachannel"
            pass

        self.context.term()

    def reset(self):
        # Socket is confused. Close and remove it.
        self.close()
        self.init()

    def sendcmd(self, cmd, **args):
        data = "4%s"%ujson.dumps([cmd, args])
        data = self.sendMsgOverCMDChannel(data)

        result = ujson.loads(data)
        print result
        if result["state"] == "ok":
            return result["result"]
        elif result["state"] == "nomethod":
            msg="execution error on server:%s on %s:%s.\n Could not find method:%s\n"%(self.servername,self.ipaddr,self.port,cmd)
            o.errorconditionhandler.raiseBug(msgpub="msg",message="",category="rpc.exec")
        else:
            eco=o.errorconditionhandler.getErrorConditionObject(result["result"])
            msg="execution error on server:%s on %s:%s.\nCmd:%s\nargs:\n%s\nErrorGUID=%s"%(self.servername,self.ipaddr,self.port,cmd,args,eco.guid)
            o.errorconditionhandler.raiseOperationalCritical(msgpub="",message=msg,category="rpc.exec",die=True,tags="ecoguid:%s"%eco.guid)            
            # raise RuntimeError("error in send cmd (error on server):%s, %s"%(cmd, result["result"]))

    # def sendcmdData(self, cmd, **args):
    #     data = "4%s"%ujson.dumps([cmd, args])
    #     self.datachannel.send(data)


    def perftest(self):
        start = time.time()
        nr = 10000
        print "start perftest for %s for raw ping"%nr
        for i in range(nr):
            if not self.sendMsgOverCMDChannel("ping") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr/(stop-start)
        print "nr items per sec: %s"%nritems
        print "start perftest for %s for cmd ping"%nr
        for i in range(nr):
            if not self.sendcmd("pingcmd") == "pong":
                raise RuntimeError("ping did not return pong.")
        stop = time.time()
        nritems = nr/(stop-start)
        print "nr items per sec: %s"%nritems
