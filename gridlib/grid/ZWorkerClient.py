from OpenWizzy import o
import zmq.green as zmq
import inspect
import struct
ujson = o.db.serializers.ujson
from ZDaemonClient import ZDaemonClient


class ZWorkerClient():
    def __init__(self,ipaddr="localhost", retry=True):
        #client to talk with broker over standard zdaemon communication channel
        self.brokerclient=ZDaemonClient(ipaddr=ipaddr,port=5554,servername="broker")

        self.serverEndpoint = "tcp://%s:5555"%ipaddr
        self.requestTimeout = 100*1000  # 100 sec

        self.actions = {}

        self.retry = retry        

        self.init()


    def init(self):

        self.context = zmq.Context(1)

        self.log("Connecting to zserver", "zmq.client")
        self.socket = self.context.socket(zmq.REQ)

        self.log("zclient connects to %s"%(self.serverEndpoint), "zmq.client")
        self.socket.connect(self.serverEndpoint)

        self.log("ZMQ client got as clientid: %s" % o.application.whoAmI, level=8, category="master.start")
        
        self.socket.setsockopt(zmq.IDENTITY, o.application.getWhoAmiStr())

        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def log(self, msg, category="", level=4):
        o.logger.log(msg, level=level, category=category)
        # print msg

    def close(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()
        self.poll.unregister(self.socket)
        self.context.term()

    def reset(self):
        # Socket is confused. Close and remove it.
        self.close()
        self.init()

    def send(self, msg):
        if self.retry:
            while True:
                print "Send (%s)" % msg
                self.socket.send(msg)
                expect_reply = True
                while expect_reply:
                    socks = dict(self.poll.poll(self.requestTimeout))
                    if socks.get(self.socket) == zmq.POLLIN:
                        reply = self.socket.recv()
                        if not reply:
                            break
                        else:
                            return reply
                    else:
                        print "W: No response from server, retrying"
                        self.reset()
                        self.socket.send(msg)
            return reply
        else:
            print "Send once (%s)" % msg
            self.socket.send(msg)
            socks = dict(self.poll.poll(self.requestTimeout))
            if socks.get(self.socket) == zmq.POLLIN:
                return self.socket.recv()
            else:
                o.errorconditionhandler.raiseOperationalCritical(message="", category="",
                                                                 msgpub="could not communicate with server on %s"%self.serverEndpoint, die=True, tags="")

    def registerAction(self, action):
        """
        register action with broker if not done yet
        """
        ukey=action.getUniqueKey()
        if ukey in self.actions:
            return self.actions[ukey]
        else:
            id = self.brokerclient.sendcmd("registerAction", action=action)
            action.id = id
            action.getSetGuid()
            self.actions[ukey] = action
            return action

    def do(self, jfunction, jname="", executorrole="*", jcategory="", jerrordescr="", jrecoverydescr="", jmaxtime=0,
           jwait=True, masterid=0,parentid=0,allworkers=True, **args):
        """
        @param allworkers if False then only one of the workers need to reply and execute the work (is of the role specified)
        """

        source = inspect.getsource(jfunction)
        filepath = inspect.getabsfile(jfunction)

        if jcategory == "" or jname=="":
            methodname = source.split("\n")[0].split("def")[1].split("(")[0].strip()
            source = source.replace(methodname, "jfunc")
            jcategory = "method.%s"%methodname

            if jname=="":
                jname=methodname

        action=o.core.grid.zobjects.getZActionObject(name=jname,
                         code=source, path=filepath,
                         category=jcategory, errordescr=jerrordescr,
                         recoverydescr=jrecoverydescr, maxtime=jmaxtime)

        action = self.registerAction(action)

        job = o.core.grid.zobjects.getZJobObject(executorrole=executorrole, actionid=action.id, args=args,jidmaster=masterid,jidparent=parentid,allworkers=allworkers)
        
        returnjob = self.send(o.db.serializers.ujson.dumps(job.__dict__))
        returnjob=ujson.loads(returnjob)
        job = o.core.grid.zobjects.getZJobObject(ddict=returnjob)

        if job.state=="workernotfound":
            o.errorconditionhandler.raiseOperationalCritical(msgpub="Could not find worker to execute work.",message="work not executed was: %s"%job,category="worker.execute",die=True,tags="jobguid:%s"%job.guid)
        elif job.state=="error":
            msg="Error in worker execution of %s. Job guid was:%s.\nError was:%s."%(jname,job.guid,job.errordescr)
            o.errorconditionhandler.raiseBug(message=msg,category="worker.client",tags="jobguid:%s"%job.guid)
        elif job.state=="ok":
            return job.result
        else:
            o.errorconditionhandler.raiseBug(message="job state unknown",category="worker.client")
            

    def registerWorker(self,obj,roles,instance,identity):
        return self.brokerclient.sendcmd("registerWorker",obj=obj.__dict__,roles=roles,instance=instance,identity=identity)

    def getactivejobs(self):
        return self.brokerclient.sendcmd("getactivejobs")

    def ping(self):
        return self.brokerclient.sendcmd("ping")

