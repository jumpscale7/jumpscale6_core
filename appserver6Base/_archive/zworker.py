#
##  Paranoid Pirate worker
#
#   Author: Daniel Lundin <dln(at)eintr(dot)org>
#
from pylabs.InitBase import *
import os
import time

q.application.appname = "zworker"
q.application.start()

from random import randint
import time
import ujson
import zmq

HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 5

#  Paranoid Pirate Protocol constants
PPP_READY = "\x01"      # Signals worker is ready
PPP_HEARTBEAT = "\x02"  # Signals worker heartbeat

def worker_socket(context, poller):
    """Helper function that returns a new configured socket
       connected to the Paranoid Pirate queue"""
    worker = context.socket(zmq.DEALER) # DEALER
    identity = "1_2"
    worker.setsockopt(zmq.IDENTITY, identity)
    poller.register(worker, zmq.POLLIN)
    worker.connect("tcp://localhost:5556")
    worker.send(PPP_READY)
    return worker

context = zmq.Context(1)
poller = zmq.Poller()

liveness = HEARTBEAT_LIVENESS
interval = INTERVAL_INIT

heartbeat_at = time.time() + HEARTBEAT_INTERVAL

from ZJob import *

class Worker():
    def __init__(self,workersocket):
        self.jfunctions={}


    def register(self,nodeid,workeridOnNode,roles):
        return self._sendcmd("register",nodeid=nodeid,workeridOnNode=workeridOnNode,roles=roles)          

    def process(self,jobobj):
        if self.jfunctions.has_key(jobobj.defmd5):
            jfunc=self.jfunctions[jobobj.defmd5]
        else:
            try:
                exec(jobobj.defcode)            
            except Exception,e:
                jobobj.state="error"
                jobobj.errordescr="Syntax error probably in def, check the code & try again. Could not import.Error was:\n%s"%e
                return jobobj
            self.jfunctions[jobobj.defmd5]=jfunc

        jobobj.jresult=jfunc(**jobobj.defargs)
        jobobj.state="ok"
        return jobobj        



workersocket = worker_socket(context, poller)
worker=Worker(workersocket)
cycles = 0
while True:
    socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

    # Handle worker activity on backend
    if socks.get(workersocket) == zmq.POLLIN:
        #  Get message
        #  - 3-part envelope + content -> request
        #  - 1-part HEARTBEAT -> heartbeat
        frames = workersocket.recv_multipart()

        if not frames:
            break # Interrupted        

        if len(frames) > 1:
            # print "I: Normal reply"
            job=ZJob()
            job.loads(frames[1])
            job=worker.process(job)
            frames[1]=job.dumps()

            workersocket.send_multipart(frames)
            liveness = HEARTBEAT_LIVENESS

        elif len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
            # print "I: Queue heartbeat"
            liveness = HEARTBEAT_LIVENESS
        else:
            print "E: Invalid message: %s" % frames
        interval = INTERVAL_INIT
    else:
        liveness -= 1
        if liveness == 0:
            print "W: Heartbeat failure, can't reach queue"
            print "W: Reconnecting in %0.2fs" % interval
            time.sleep(interval)

            if interval < INTERVAL_MAX:
                interval *= 1.5
            poller.unregister(workersocket)
            workersocket.setsockopt(zmq.LINGER, 0)
            workersocket.close()
            workersocket = worker_socket(context, poller)
            liveness = HEARTBEAT_LIVENESS
    if time.time() > heartbeat_at:
        heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        print "I: Worker heartbeat"
        workersocket.send(PPP_HEARTBEAT)