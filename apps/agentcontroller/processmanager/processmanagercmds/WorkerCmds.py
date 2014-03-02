from JumpScale import j
import time

class WorkerCmds():

    def __init__(self,daemon=None):
        self._name="worker"
        if not daemon:
            return
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth

    def getQueuedJobs(self,queue="default",format="json",session=None):        
        """
        @format can be json or wiki
        @queue normally we have default,io,hypervisor
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class see getQueuedJobs
        #only use local redis on port 6678
        
    def getFailedJobs(self,hoursago=0,format="json",session=None):
        """
        @hoursago : only show failed jobs from X hours ago, if 0 then all
        @format can be json or wiki
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class make new method
        #only use local redis on port 6678

    def removeJobs(self,hoursago=48,failed=False):
        """
        walk over jobs, remove jobs which are older than the specified hours
        if failed = True then also remove the failed jobs
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd) 

    def resetQueue(self,queue="default",hoursago=0):
        """
        @param queue, if "" then all queues
        if hoursago==0 then all items in queue
        """

    def resubmitJob(self,jobid):
        """
        job which failed or had timeout, can be resubmitted to queue, so it can be executed again
        """

    def checkTimeouts(self):
        """
        walk over all jobs in queue & not in queue, check that timeout is not expired, if expired, put job in failed mode 
        if job failed and on queue, remove put to jobs
        """

    def getJob(self,session=None):        
        """
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class make new method
        #only use local redis on port 6678

