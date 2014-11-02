#
# Paranoid Pirate worker
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof@incubaid.com
#

from JumpScale import j
from ..gevent.GeventLoop import GeventLoop
import time
import zmq
from ZWorkerClient import ZWorkerClient
ujson = j.db.serializers.getSerializerType('j')


class ZWorker(GeventLoop):

    def __init__(self, addr, port, instance=1, roles=["system"], category=""):
        GeventLoop.__init__(self)
        self.server = addr
        self.port = port
        self.actions = {}
        self.instance = instance
        self.roles = roles
        self.category = category
        self.jfunctions = {}

        self.HEARTBEAT_LIVENESS = 3  # amounts of times before hardbeat fails
        self.HEARTBEAT_INTERVAL = 1  # time to wait on poll
        self.INTERVAL_INIT = 1  # seconds wait before init
        self.INTERVAL_MAX = 5

        #  Paranoid Pirate Protocol constants
        self.PPP_READY = "\x01"      # Signals worker is ready
        self.PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

        self.schedule("timer", self._timer)

        self.interval = self.INTERVAL_INIT

        self.heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL

        self.init()

    def init(self):

        self.liveness = self.HEARTBEAT_LIVENESS

        self.client = ZWorkerClient(ipaddr=self.server)

        self.identity = "%s_%s_%s_%s" % (j.core.grid.processobject.gid, j.core.grid.processobject.bid, j.core.grid.processobject.nid, self.instance)

        self.client.registerWorker(obj=j.core.grid.processobject, roles=self.roles, instance=self.instance, identity=self.identity)

        j.logger.log("worker:%s, roles:%s" % (self.identity, self.roles), level=3, category="zworker.init")

        self.context = zmq.Context(1)
        self.poller = zmq.Poller()

        self.initWorkerSocket()

    def initWorkerSocket(self):
        """Helper function that returns a new configured socket
           connected to the Paranoid Pirate queue"""
        self.worker = self.context.socket(zmq.DEALER)  # DEALER
        # self.identity = "%s_%s_%s"%(j.core.grid.nid,self.instance,self.workerid)
        self.worker.setsockopt(zmq.IDENTITY, self.identity)
        self.poller.register(self.worker, zmq.POLLIN)
        self.worker.connect("tcp://%s:%s" % (self.server, self.port))
        self.worker.send(self.PPP_READY)
        j.logger.log("zmq socket ready, identity:%s" % self.identity, level=5, category="zworker.init")

    def process(self, jobobj):
        if self.actions.has_key(jobobj.actionid):
            action = self.actions[jobobj.actionid]
        else:
            action = self.client.brokerclient.sendcmd("getAction", actionid=jobobj.actionid)
            action = j.core.grid.zobjects.getZActionObject(action)
            action.codemd5 = str(action.codemd5)
            self.actions[jobobj.actionid] = action

        if self.jfunctions.has_key(action.codemd5):
            jfunc = self.jfunctions[action.codemd5]
        else:
            try:
                exec(action.code)
            except Exception, e:
                eco = j.errorconditionhandler.parsePythonErrorObject(e)
                eco.descriptionpub = "Syntax error probably in def, check the code & try again. Could not import, action id = %s" % action.id
                eco.code = action.code
                eco.process()
                jobobj.state = "error"
                jobobj.errordescr = "%s Error was:\n%s" % (eco.descriptionpub, e)
                return jobobj
            self.jfunctions[action.codemd5] = jfunc

        try:
            jobobj.result = jfunc(**jobobj.args)
        except Exception, e:
            eco = j.errorconditionhandler.parsePythonErrorObject(e)
            eco.errormessagePub = "Execution error, check the code, action id = %s" % action.id
            eco.code = action.code
            eco.process()
            jobobj.ecid = eco.guid
            jobobj.state = "error"
            jobobj.errordescr = "%s Error was:\n%s" % (eco.errormessagePub, e)
            return jobobj
        jobobj.state = "ok"
        return jobobj

    def reset(self):

        # print reset worker
        j.errorconditionhandler.raiseOperationalWarning(msgpub="reset zworker", category="zbroker")
        self.poller.unregister(self.worker)
        self.worker.setsockopt(zmq.LINGER, 0)
        self.worker.close()

        self.client.socket.setsockopt(zmq.LINGER, 0)
        self.client.socket.close()

        self.init()  # restart process

        # self.liveness = self.HEARTBEAT_LIVENESS

    def start(self):
        cycles = 0
        while True:
            socks = dict(self.poller.poll(1000 * self.HEARTBEAT_INTERVAL))  # wait in miliseconds

            # Handle worker activity on backend
            if socks.get(self.worker) == zmq.POLLIN:
                #  Get message
                #  - 3-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = self.worker.recv_multipart()

                if not frames:
                    break  # Interrupted

                if len(frames) > 1:

                    data = frames[1]

                    jobDict = ujson.loads(data)
                    job = j.core.grid.zobjects.getZJobObject(ddict=jobDict)

                    job = self.process(job)

                    frames[1] = ujson.dumps(job.__dict__)

                    self.worker.send_multipart(frames)
                    self.liveness = self.HEARTBEAT_LIVENESS

                elif len(frames) == 1 and frames[0] == self.PPP_HEARTBEAT:
                    # print "heartbeat received from broker"
                    self.liveness = self.HEARTBEAT_LIVENESS
                else:
                    msg = "E: Invalid message: %s" % frames
                    j.errorconditionhandler.raiseOperationalWarning(msgpub="error in message send to zworker", message=msg, category="zbroker")
                self.interval = self.INTERVAL_INIT
            else:
                self.liveness -= 1
                if self.liveness == 0:
                    j.logger.log("ZWorker heartbeat failure or could not connect to broker, reconnecting in %0.2fs" %
                                 self.interval, level=3, category="zworker.connection")
                    time.sleep(self.interval)

                    if self.interval < self.INTERVAL_MAX:
                        self.interval *= 1.5

                    self.reset()

            if time.time() > self.heartbeat_at:
                self.heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL
                # print "I: Worker send heartbeat"
                self.worker.send(self.PPP_HEARTBEAT)
