#
##  Paranoid Pirate queue
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof Incubaid BVBA Belgium
#
from pylabs.InitBase import q
q.application.appname = "zworker"
q.application.start()
import time
import struct

import zmq

from grid.ZDataProcessor import ZDataProcessor
from grid.ZObjects import ZJob, ZAction, ZWorker, ZMaster, ZNode
from grid.ZClient import ZClient

class BrokerInterface():

    def __init__(self,broker):
        self.broker=broker
        self.registerObjectcategory=self.broker.dp.registerObjectcategory
        self.registerObject=self.broker.dp.registerObject
        self.methods={}

    def getactivejobs(self):
        return self.broker.activeJobs

    def ping(self):
        return "pong"
        

class Broker():
    def __init__(self):
        self.workers=[] 
        self.role2workers={}
        self.role2workersAvailable={}
        self.activeJobs={}
        self.loggers={}
        dbinc=q.db.keyvaluestore.getFileSystemStore("broker","ids",serializers=[q.db.serializers.int])
        dbfs=q.db.keyvaluestore.getFileSystemStore("broker","obj",serializers=[])
        self.dp=ZDataProcessor(self,dbinc,dbfs)

        self.remoteInterface=BrokerInterface(self)

        self.HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
        self.HEARTBEAT_INTERVAL = 1.0   # Seconds

        #  Paranoid Pirate Protocol constants
        self.PPP_READY = "\x01"      # Signals worker is ready
        self.PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

        self.context = zmq.Context(1)

        self.frontend = self.context.socket(zmq.ROUTER) # ROUTER
        self.backend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.frontend.bind("tcp://*:5555") # For clients
        self.backend.bind("tcp://*:5556")  # For workers

        self.poll_workers = zmq.Poller()
        self.poll_workers.register(self.backend, zmq.POLLIN)

        self.poll_both = zmq.Poller()
        self.poll_both.register(self.frontend, zmq.POLLIN)
        self.poll_both.register(self.backend, zmq.POLLIN)

        self.heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL

        self.now=0000


    def registerRole4NewWorker(self,workerid,rolestr):
        rolestr=rolestr.lower()
        if not self.role2workers.has_key(rolestr):
            self.role2workers[rolestr]=[]
        if not self.role2workersAvailable.has_key(rolestr):
            self.role2workersAvailable[rolestr]=[]

        self.role2workers[rolestr].append(int(workerid))
        self.role2workersAvailable[rolestr].append(int(workerid))

    # def register(self,nodeid,workeridOnNode,roles):
    #     # print "REGISTER:%s"%workerid
    #     w=Worker(nodeid,workeridOnNode,roles)
    #     self.workers.append(w)
    #     w.id=len(self.workers)-1
    #     for role in roles:
    #         self.registerRole4NewWorker(w.id,role)
    #     return w

    def getWork(self,job):

        role=str(job["executorrole"])
        if role=="*":
            workers=[item.guid for item in self.workers]
        
        jobguids=[]

        if len(workers)==1:
            self.activeJobs[job["guid"]]=job
            jobguids=[job["guid"]]
            job["agent"]=workers[0]   
        else:
            self.activeJobs[job["guid"]]=job
            job["children"]=[]
            for worker in workers:
                job["guid"]=q.base.idgenerator.generateGUID()
                job["agent"]=worker                
                jobguids.append(job["guid"])
                self.activeJobs[job["guid"]]=job

        return jobguids

        
    def hasWorkers(self):
        return self.workers<>[]

    def registerTypesOfZobjects(self):
        """
        register different type of native objects we are going to use
        """
        for item in [ZJob,ZAction,ZMaster,ZWorker,ZNode,ZClient]:
            r=item()            
            self.dp.registerObjectcategory(r.getCategory(),r.getProcessingParams())

    def start(self):

        self.registerTypesOfZobjects()

        # self.schedule("timer",self._timer)

        print "broker started"

        while True:
            # if Broker.hasWorkers() > 0:
            #     poller = poll_both
            # else:
            #     poller = poll_workers

            poller = self.poll_both
            socks = dict(poller.poll(self.HEARTBEAT_INTERVAL * 1))

            ##############
            # Handle worker activity on backend
            if socks.get(self.backend) == zmq.POLLIN:
                # print "activity on backend"
                # Use worker address for LRU routing
                frames = self.backend.recv_multipart()
                if not frames:
                    break

                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) == 1:
                    if msg[0] not in (self.PPP_READY, self.PPP_HEARTBEAT):
                        print "E: Invalid message from worker: %s" % msg
                else:
                    # print "reply to client:%s"%msg
                    #msg here is what returns from worker            
                    job=ujson.loads(msg[1])
                    if job["state"]=="ok":
                        self.activeJobs.pop(job["guid"])
                    if job["parent"]=="":
                        # msg[1]=ujson.dumps(job)
                        self.frontend.send_multipart([msg[0],"",msg[1]])
                    else:
                        #keep track of other parts which need to come
                        from pylabs.Shell import ipshellDebug,ipshell
                        print "DEBUG NOW other parts"
                        ipshell()
                        

                # Send heartbeats to idle workers if it's time
                if self.now >= self.heartbeat_at:
                    for worker in self.workers:
                        msg = [worker.guid, self.PPP_HEARTBEAT]
                        print "send heartbeat to %s"%worker.guid
                        self.backend.send_multipart(msg)
                    self.heartbeat_at = self.now + self.HEARTBEAT_INTERVAL

            ##############
            #receive info from client
            if socks.get(self.frontend) == zmq.POLLIN:
                # print "activity on frontend"
                frames = self.frontend.recv_multipart()
                if not frames:
                    break

                oid=struct.unpack_from("<i",frames[2],0)[0]
                data=frames[2][4:]
                if oid==4:
                    #is rpc message from client
                    self.frontend.send_multipart([frames[0],"",ujson.dumps(self.processRPC(data))])
                elif oid==2:
                    #is job message
                    self.processJob(data)
                elif oid==5:
                    self.processObject(data)
                elif oid==999:
                    return


    def processObject(self,data):        
        return self.dp.registerObject(objectcategory,data,objectguid,overwrite=True)

    def processRPC(self,data):
        cmd=ujson.loads(data) #list with item 0=cmd, item 1=args
        cmd2={}
        if self.remoteInterface.methods.has_key(cmd[0]):
            ffunction=self.remoteInterface.methods[cmd[0]]
        else:
            try:
                ffunction=eval("self.remoteInterface.%s"%cmd[0])

            except RuntimeError,e:
                cmd2["state"]="error"
                cmd2["result"]="cannot find cmd %s on Brokerinterface."%cmd[0]
                return cmd2
            self.remoteInterface.methods[cmd[0]]=ffunction
        result=ffunction(**cmd[1])
        try:
            result=ffunction(**cmd[1])
        except Exception,e:
            cmd2["state"]="error"            
            cmd2["result"]=str(e)
            return cmd2
        cmd2["state"]="ok"
        cmd2["result"]=result
        return cmd2


    def processJob(self,data):
        from pylabs.Shell import ipshellDebug,ipshell
        print "DEBUG NOW processjob"
        ipshell()
        
        try:
            job=ujson.decode(data)
        except:
            raise RuntimeError("Could not decode msg,%s"%msg)

        if job.has_key("cmd"):
            job=self.executecmdMsg(job)            
            self.frontend.send_multipart([frames[0],"",ujson.dumps(job)])
        else:            
            jobguids=self.getWork(job)

            forward=True

            ###############
            #SEND TO WORKER
            if forward:           
                # frames.insert(0, "")
                for guid in jobguids:     
                    guid=str(guid)           
                    # frames[0]=str(Broker.activeJobs[guid]["agent"])
                    # frames[2]=str(ujson.dumps(Broker.activeJobs[guid]))
                    # print frames
                    # print ujson.dumps(Broker.activeJobs[guid])
                    # print "send worker for job coming from client: %s" % frames[0]
                    self.backend.send_multipart([self.activeJobs[guid]["agent"],frames[0],ujson.dumps(self.activeJobs[guid])])


def test():
    broker=Broker()
    broker.start()

locals={}
# locals["params"]=broker
locals["q"]=q
locals["test"]=test
do=q.tools.performancetrace.profile('test()', locals)
