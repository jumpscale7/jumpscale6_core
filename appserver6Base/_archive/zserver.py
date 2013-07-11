#
##  Paranoid Pirate queue
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#   Author: Kristof Incubaid BVBA Belgium
#
from pylabs.InitBase import *
q.application.appname = "zworker"
q.application.start()

import ujson
import copy

from collections import OrderedDict
import time
import zmq

HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
HEARTBEAT_INTERVAL = 1.0   # Seconds

#  Paranoid Pirate Protocol constants
PPP_READY = "\x01"      # Signals worker is ready
PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

class Worker(object):
    def __init__(self, address):
        self.address = address
        self.expiry = time.time() + HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS

class GridInterface():

    def __init__(self,grid):
        self.grid=grid
        self.register=grid.register

    def getactivejobs(self):
        return self.grid.activeJobs

    def ping(self):
        return "pong"


class Worker():
    def __init__(self,nodeid,workeridOnNode,roles=[]):
        self.id=0
        self.nodeid=nodeid
        self.workeridOnNode=workeridOnNode
        self.roles=roles

    def dumps(self):
        # return msgpack.dumps(self.__dict__)
        return ujson.dumps(self.__dict__)

    def loads(self,s):
        # self.__dict__.update(msgpack.loads(s))
        self.__dict__.update(ujson.loads(s))

    __str__=dumps
    __repr__=dumps        

class Grid(object):
    def __init__(self):
        self.workers=[]
        self.role2workers={}
        self.role2workersAvailable={}
        self.activeJobs={}
        self.remoteInterface=GridInterface(self)

    def executecmdMsg(self,cmd):

        try:
            ffunction=eval("self.remoteInterface.%s"%cmd["cmd"])
        except RuntimeError,e:
            cmd["state"]="error"
            cmd["result"]="cannot find cmd %s on gridinterface."%cmd["cmd"]
            return cmd
        try:
            result=ffunction(**cmd["args"])
        except Exception,e:
            cmd["state"]="error"
            cmd["result"]=e
        cmd["state"]="ok"
        cmd["result"]=result
        return cmd

    def registerRole4NewWorker(self,workerid,rolestr):
        rolestr=rolestr.lower()
        if not self.role2workers.has_key(rolestr):
            self.role2workers=[]
        if not self.role2workersAvailable.has_key(rolestr):
            self.role2workersAvailable=[]
        self.role2workers[rolestr].append(int(workerid))
        self.role2workersAvailable[rolestr].append(int(workerid))

    def register(self,nodeid,workeridOnNode,roles):
        # print "REGISTER:%s"%workerid
        w=Worker(nodeid,workeridOnNode,roles)
        self.workers.append(w)
        w.id=len(self.workers)-1
        for role in roles:
            self.registerRole4NewWorker(w.id,role)
        return w

    def getWork(self,job):

        role=str(job["executorrole"])
        if role=="*":
            workers=self.workers.keys()
        
        jobguids=[]

        if len(workers)==1:
            self.activeJobs[job["guid"]]=job
            jobguids=[job["guid"]]
            job["agent"]=workers[0]   
        else:
            self.activeJobs[job["guid"]]=job
            job2=copy.copy(job)
            job["children"]=[]
            for worker in workers:
                job["guid"]=q.base.idgenerator.generateGUID()
                job["agent"]=worker                
                jobguids.append(job["guid"])
                self.activeJobs[job["guid"]]=job

        return jobguids

        
    def hasWorkers(self):
        return True
        return self.nodes<>{}


context = zmq.Context(1)

frontend = context.socket(zmq.ROUTER) # ROUTER
backend = context.socket(zmq.ROUTER)  # ROUTER
frontend.bind("tcp://*:5555") # For clients
backend.bind("tcp://*:5556")  # For workers

poll_workers = zmq.Poller()
poll_workers.register(backend, zmq.POLLIN)

poll_both = zmq.Poller()
poll_both.register(frontend, zmq.POLLIN)
poll_both.register(backend, zmq.POLLIN)

grid=Grid()

heartbeat_at = time.time() + HEARTBEAT_INTERVAL

print "worker controller started"

while True:
    if grid.hasWorkers() > 0:
        poller = poll_both
    else:
        poller = poll_workers
    socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

    ##############
    # Handle worker activity on backend
    if socks.get(backend) == zmq.POLLIN:
        # print "activity on backend"
        # Use worker address for LRU routing
        frames = backend.recv_multipart()
        if not frames:
            break

        # Validate control message, or return reply to client
        msg = frames[1:]
        if len(msg) == 1:
            if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
                print "E: Invalid message from worker: %s" % msg
        else:
            # print "reply to client:%s"%msg
            #msg here is what returns from worker            
            job=ujson.loads(msg[1])
            if job["state"]=="ok":
                grid.activeJobs.pop(job["guid"])
            if job["parent"]=="":
                # msg[1]=ujson.dumps(job)
                frontend.send_multipart([msg[0],"",msg[1]])
            else:
                #keep track of other parts which need to come
                from pylabs.Shell import ipshellDebug,ipshell
                print "DEBUG NOW other parts"
                ipshell()
                

        # Send heartbeats to idle workers if it's time
        if time.time() >= heartbeat_at:
            for worker in grid.workers.keys():
                msg = [worker, PPP_HEARTBEAT]
                print "send heartbeat to %s"%worker
                backend.send_multipart(msg)
            heartbeat_at = time.time() + HEARTBEAT_INTERVAL

    ##############
    #receive info from client
    if socks.get(frontend) == zmq.POLLIN:
        # print "activity on frontend"
        frames = frontend.recv_multipart()
        if not frames:
            break

        try:
            job=ujson.decode(frames[2])
        except:
            raise RuntimeError("Could not decode msg,%s"%msg)

        if job.has_key("cmd"):
            job=grid.executecmdMsg(job)            
            frontend.send_multipart([frames[0],"",ujson.dumps(job)])
        else:            
            jobguids=grid.getWork(job)

            forward=True

            ###############
            #SEND TO WORKER
            if forward:           
                # frames.insert(0, "")
                for guid in jobguids:     
                    guid=str(guid)           
                    # frames[0]=str(grid.activeJobs[guid]["agent"])
                    # frames[2]=str(ujson.dumps(grid.activeJobs[guid]))
                    # print frames
                    # print ujson.dumps(grid.activeJobs[guid])
                    # print "send worker for job coming from client: %s" % frames[0]
                    backend.send_multipart([grid.activeJobs[guid]["agent"],frames[0],ujson.dumps(grid.activeJobs[guid])])

