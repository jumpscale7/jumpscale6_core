from JumpScale import j
import time
import JumpScale.baselib.redisworker
import ujson

class WorkerCmds():

    def __init__(self,daemon=None):
        self._name="worker"
        if not daemon:
            return
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.redisworker = j.clients.redisworker

    def getQueuedJobs(self,queue="default", format="json", session=None):
        """
        @format can be json or wiki
        @queue normally we have default,io,hypervisor
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if format == 'json':
            return ujson.dumps(self.redisworker.getQueuedJobs(queue=queue, asWikiTable=False))
        else:
            return self.redisworker.getQueuedJobs(queue=queue)
        
        
    def getFailedJobs(self, queue=None, hoursago=0, format='json', session=None):
        """
        @hoursago : only show failed jobs from X hours ago, if 0 then all
        @format can be json or wiki
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if format == 'json':
            return ujson.dumps(self.redisworker.getFailedJobs(queue=queue, hoursago=hoursago))
        else:
            return self.redisworker.getFailedJobs(queue=queue, hoursago=hoursago)
        

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

