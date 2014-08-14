#
# Paranoid Pirate queue
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof Incubaid BVBA Belgium
#
from JumpScale import j

import time
import copy

import zmq.green as zmq
# from ZDataProcessor import ZDataProcessor
from ..gevent.GeventLoop import GeventLoop

from BrokerMainActions import BrokerMainActions

from ..zdaemon.ZDaemon import ZDaemon
import JumpScale.grid.grid

ujson = j.db.serializers.getSerializerType('j')


class ZBroker(ZDaemon):

    def __init__(self):
        ZDaemon.__init__(self)
        self.daemon.broker = self
        self.workers = {}  # key = worker.id = process.id (process id of worker which is unique) also called workerid, value is the set of roles
        self.role2workers = {}
        self.role2workersAvailable = {}
        self.activeJobs = {}

        self.actions = {}

        self.addCMDsInterface(BrokerMainActions, category='broker')

        self.HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
        self.HEARTBEAT_INTERVAL = 1.0   # Seconds

        #  Paranoid Pirate Protocol constants
        self.PPP_READY = "\x01"      # Signals worker is ready
        self.PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

        self.context = zmq.Context(1)

        self.frontend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.backend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.frontend.bind("tcp://*:5651")  # For clients
        self.backend.bind("tcp://*:5650")  # For workers

        self.poll_workers = zmq.Poller()
        self.poll_workers.register(self.backend, zmq.POLLIN)

        self.poll_both = zmq.Poller()
        self.poll_both.register(self.frontend, zmq.POLLIN)
        self.poll_both.register(self.backend, zmq.POLLIN)

        self.heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL

        if j.core.grid.id == None:
            raise RuntimeError("Could not find grid id at j.core.grid.id, means grid not configured?")

    def registerRole4NewWorker(self, workerid, rolestr):
        rolestr = str(rolestr).lower()
        if rolestr not in self.role2workers:
            self.role2workers[rolestr] = []
        if rolestr not in self.role2workersAvailable:
            self.role2workersAvailable[rolestr] = []

        self.role2workers[rolestr].append(str(workerid))
        self.role2workersAvailable[rolestr].append(str(workerid))

    def hasWorkers(self):
        return self.workers != {}

    def start(self):

        j.logger.consoleloglevel = 7

        port = j.core.grid.config.getInt("osis.port")
        ip = j.core.grid.config.get("osis.ip")
        nsid = j.core.grid.config.getInt("grid.broker.id")

        osisclient = j.core.osis.getClient(ip, port, user='root')
        if nsid == 0:
            nsname, nsid = osisclient.createNamespace(name="broker_", template="coreobjects", incrementName=True)
            j.core.grid.config.set("grid.broker.id", nsid)
        else:
            if not osisclient.existsNamespace("broker_%s" % nsid):
                # namespace does not exist yet on server
                nsname, nsid = osisclient.createNamespace(name="broker_", template="coreobjects", incrementName=True, nsid=nsid)
                j.core.grid.config.set("grid.broker.id", nsid)

        self.id = nsid

        self.osis_node = j.core.osis.getClientForCategory("broker_%s" % nsid, "node", ip, port)
        # self.osis_job=j.core.osis.getClientForCategory("broker_%s"%nsid,"job",ip,port)
        self.osis_process = j.core.osis.getClientForCategory("broker_%s" % nsid, "process", ip, port)
        self.osis_application = j.core.osis.getClientForCategory("broker_%s" % nsid, "applicationtype", ip, port)
        self.osis_action = j.core.osis.getClientForCategory("broker_%s" % nsid, "action", ip, port)

        j.core.grid.init(broker=self)  # makes sure we dont connect over ip

        self.schedule("cmdGreenlet", self.cmdGreenlet)
        self.startClock()

        j.logger.log("broker started", level=3, category="grid.broker")

        while True:
            # if self.hasWorkers() > 0:
            #     poller = self.poll_both
            # else:
            #     poller = self.poll_workers

            poller = self.poll_both

            socks = dict(poller.poll(500000))  # wait for 5 seconds

            #
            # Handle worker activity on backend
            if socks.get(self.backend) == zmq.POLLIN:
                # print "activity on backend (workers)"

                frames = self.backend.recv_multipart()

                if not frames:
                    break

                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) == 1:
                    if msg[0] not in (self.PPP_READY, self.PPP_HEARTBEAT):
                        print "E: Invalid message from worker: %s" % msg
                else:
                    # print "reply from worker:%s"%msg
                    # msg here is what returns from worker

                    job = ujson.loads(msg[1])

                    if job["parent"] == 0:
                        # msg[1]=ujson.dumps(job)
                        self.frontend.send_multipart([msg[0], "", msg[1]])
                    else:
                        # keep track of other parts which need to come
                        from JumpScale.core.Shell import ipshell
                        print "DEBUG NOW other parts"
                        ipshell()

                    if job["state"] == "ok":
                        self.activeJobs.pop(job["guid"])

                # Send heartbeats to idle workers if it's time
                # print str(self.now) + " " + str(self.heartbeat_at)
                if self.now >= self.heartbeat_at:
                    for workerid in self.workers.keys():
                        msg = [str(workerid), self.PPP_HEARTBEAT]
                        # print "send heartbeat to %s"%worker.guid
                        self.backend.send_multipart(msg)
                    self.heartbeat_at = self.now + self.HEARTBEAT_INTERVAL

            #
            # receive job from client
            if socks.get(self.frontend) == zmq.POLLIN:
                # print "activity on frontend (client)"
                frames = self.frontend.recv_multipart()
                if not frames:
                    break
                data = frames[2]  # is serialized job
                try:
                    job = ujson.loads(data)
                except:
                    raise RuntimeError("Could not decode msg,%s" % data)
                self.processJob(job, client=frames[0])

    def processJob(self, job, client):

        role = str(job["executorrole"])

        if role == "*":
            workers = self.workers.keys()
        else:
            if self.role2workersAvailable.has_key(role):
                workers = self.role2workersAvailable[role]
            else:
                workers = []

        if len(workers) == 1:
            worker = workers[0]
        elif len(workers) == 0:
            # could not find workers to execute jog
            job["state"] = "workernotfound"
            job["result"] = "could not find worker to execute work, no workers known which comply to role"
            self.frontend.send_multipart([str(client), "", ujson.dumps(job)])
            return
        else:
            workerid = j.base.idgenerator.generateRandomInt(0, len(workers) - 1)
            worker = workers[workerid]

        job["wpid"] = worker
        self.activeJobs[job["guid"]] = job

        self.backend.send_multipart([str(worker), str(client), ujson.dumps(job)])
