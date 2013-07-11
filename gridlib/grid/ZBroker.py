#
##  Paranoid Pirate queue
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof Incubaid BVBA Belgium
#
from OpenWizzy import o

import time
import copy

import zmq.green as zmq
# from ZDataProcessor import ZDataProcessor
from GeventLoop import GeventLoop

from BrokerMainActions import BrokerMainActions

from ZDaemon import ZDaemon

ujson = o.db.serializers.ujson

class ZBroker(ZDaemon):
    def __init__(self):
        ZDaemon.__init__(self,port=5554)
        self.workers = {}#key = worker.id = process.id (process id of worker which is unique) also called workerid, value is the set of roles
        self.role2workers = {}
        self.role2workersAvailable = {}
        self.activeJobs = {}

        self.actions={}

        self.addCMDsInterface(BrokerMainActions)

        self.HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
        self.HEARTBEAT_INTERVAL = 1.0   # Seconds

        #  Paranoid Pirate Protocol constants
        self.PPP_READY = "\x01"      # Signals worker is ready
        self.PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

        self.context = zmq.Context(1)

        self.frontend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.backend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.frontend.bind("tcp://*:5555")  # For clients
        self.backend.bind("tcp://*:5556")  # For workers

        self.poll_workers = zmq.Poller()
        self.poll_workers.register(self.backend, zmq.POLLIN)

        self.poll_both = zmq.Poller()
        self.poll_both.register(self.frontend, zmq.POLLIN)
        self.poll_both.register(self.backend, zmq.POLLIN)

        self.heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL

        if o.core.grid.id==None:
            o.core.grid.id=o.core.grid.hrd.getInt("grid.id")

    def registerRole4NewWorker(self, workerid, rolestr):        
        rolestr = str(rolestr).lower()
        if rolestr not in self.role2workers:
            self.role2workers[rolestr] = []
        if rolestr not in self.role2workersAvailable:
            self.role2workersAvailable[rolestr] = []

        self.role2workers[rolestr].append(str(workerid))
        self.role2workersAvailable[rolestr].append(str(workerid))


    def getWork(self, job):
        # keep in dict format

        role = str(job["executorrole"])
        if role == "*":
            workers = self.workers.keys()

        jobids = [job["guid"]] 

        if len(workers) == 1:  
            job["wpid"] = workers[0]
            self.activeJobs[job["guid"]] = job
        elif len(workers)==0:
            return []
        else:
            from OpenWizzy.core.Shell import ipshellDebug,ipshell
            print "DEBUG NOW more than 1 worker"
            ipshell()
            
            self.activeJobs[job["id"]] = job
            for worker in workers:
                job2 = copy.copy(job)
                job2["guid"] = o.base.idgenerator.generateGUID()#@todo need other algoritm in line with first job guid creation
                job2["agent"] = worker
                job2["parent"] = job["id"]
                job["childrenWaiting"].append(job2["guid"])
                self.activeJobs[job["id"]] = job2
                jobids.append(job["id"])

        return jobids

    def hasWorkers(self):
        return self.workers != {}

    def start(self):

        o.logger.consoleloglevel=7

        port=o.core.grid.hrd.getInt("broker.osis.port")
        ip=o.core.grid.hrd.get("broker.osis.ip")
        nsid=o.core.grid.hrd.getInt("broker.id")
        

        osisclient=o.core.osis.getClient(ip,port)
        if nsid==0:
            nsname,nsid=osisclient.createNamespace(name="broker_",template="coreobjects", incrementName=True)
            o.core.grid.hrd.set("broker.id",nsid)
        else:
            if not osisclient.existsNamespace("broker_%s"%nsid):
                #namespace does not exist yet on server
                nsname,nsid=osisclient.createNamespace(name="broker_",template="coreobjects", incrementName=True,nsid=nsid)
                o.core.grid.hrd.set("broker.id",nsid)

        self.id=nsid

        self.osis_node=o.core.osis.getClientForCategory("broker_%s"%nsid,"node",ip,port)
        self.osis_job=o.core.osis.getClientForCategory("broker_%s"%nsid,"job",ip,port)
        self.osis_process=o.core.osis.getClientForCategory("broker_%s"%nsid,"process",ip,port)
        self.osis_application=o.core.osis.getClientForCategory("broker_%s"%nsid,"applicationtype",ip,port)
        self.osis_action=o.core.osis.getClientForCategory("broker_%s"%nsid,"action",ip,port)

        o.core.grid.init(broker=self) #makes sure we dont connect over ip

        self.schedule("cmdGreenlet", self.cmdGreenlet)
        self.startClock()

        o.logger.log("broker started", level=3, category="grid.broker")        

        while True:
            # if self.hasWorkers() > 0:
            #     poller = self.poll_both
            # else:
            #     poller = self.poll_workers

            poller = self.poll_both

            socks = dict(poller.poll(500000))  # wait for 5 seconds

            ##############
            # Handle worker activity on backend
            if socks.get(self.backend) == zmq.POLLIN:
                print "activity on backend (workers)"

                frames = self.backend.recv_multipart()
                
                if not frames:
                    break

                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) == 1:
                    if msg[0] not in (self.PPP_READY, self.PPP_HEARTBEAT):
                        print "E: Invalid message from worker: %s" % msg
                else:
                    print "reply from worker:%s"%msg
                    # msg here is what returns from worker
                    
                    job = o.db.serializers.ujson.loads(msg[1])

                    if job["parent"] == 0:
                        # msg[1]=o.db.serializers.ujson.dumps(job)
                        self.frontend.send_multipart([msg[0], "", msg[1]])
                    else:
                        # keep track of other parts which need to come
                        from OpenWizzy.core.Shell import ipshell
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

            ##############
            # receive job from client
            if socks.get(self.frontend) == zmq.POLLIN:
                print "activity on frontend (client)"
                frames = self.frontend.recv_multipart()
                if not frames:
                    break
                data = frames[2]  #is serialized job
                try:
                    job = o.db.serializers.ujson.loads(data)
                except:
                    raise RuntimeError("Could not decode msg,%s"%data)
                self.processJob(job, client=frames[0])

    def processJob(self, job, client):


        jobids = self.getWork(job)

        if jobids==[]:
            #could not find workers to execute jog
            job["state"]="workernotfound"
            job["result"]="could not find worker to execute work, no workers known which comply to role"
            self.frontend.send_multipart([str(client), "", ujson.dumps(job)])


        # frames.insert(0, "")
        for id in jobids:
            # print "send worker for job coming from client: %s" % frames[0]
            workerid=self.activeJobs[id]["wpid"]
            self.backend.send_multipart([str(workerid), str(client), o.db.serializers.ujson.dumps(self.activeJobs[id])])

        #

        # if job.has_key("actionid"):
        #     job=self.executecmdMsg(job)
        #     self.frontend.send_multipart([frames[0],"",ujson.dumps(job)])
        # else:




# locals={}
# # locals["params"]=broker
# locals["q"]=q
# locals["test"]=test
# do=o.tools.performancetrace.profile('main()', locals)
