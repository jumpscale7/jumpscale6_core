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
        self.acclient = j.clients.agentcontroller.get()
        self.redis=self.redisworker.redis

    def getQueuedJobs(self, queue="default", format="json", session=None):
        """
        @format can be json or wiki
        @queue normally we have default,io,hypervisor
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if format == 'json':
            return self.redisworker.getQueuedJobs(queue=queue, asWikiTable=False)
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
        
    def getWorkersWatchdogTime(self):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        workers2 = self.redis.hgetall("workers:watchdog")
        foundworkers={}
        for workername, timeout in zip(workers2[0::2], workers2[1::2]):    
            foundworkers[workername]=timeout
        return foundworkers

    def stopWorkers(self):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        for workername in self.getWorkersWatchdogTime.keys():
            redis.set("workers:action:%s"%workername,"STOP")

    def reloadWorkers(self):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for workername in self.getWorkersWatchdogTime.keys():
            redis.set("workers:action:%s"%workername,"RELOAD")

    def removeJobs(self, hoursago=48, failed=False, session=None):
        """
        walk over jobs, remove jobs which are older than the specified hours
        if failed = True then also remove the failed jobs
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        self.redisworker.removeJobs(hoursago=hoursago, failed=failed)

    def resetQueue(self,queue="default",hoursago=0):
        """
        @param queue, if "" then all queues
        if hoursago==0 then all items in queue
        """

    def resubmitJob(self, jobid, session=None):
        """
        job which failed or had timeout, can be resubmitted to queue, so it can be executed again
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        job = self.redisworker.getJob(jobid)
        self.redisworker.scheduleJob(job)

    def checkTimeouts(self, session=None):
        """
        walk over all jobs in queue & not in queue, check that timeout is not expired, if expired, put job in failed mode 
        if job failed and on queue, remove put to jobs
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        print "CHECKTIMEOUT"


        jobs = self.redisworker.getQueuedJobs(asWikiTable=False)
        result = list()
        for job in jobs:
            if (job['timeStart'] + job['timeout']) > j.base.time.getTimeEpoch() and job['state'] not in ('OK', 'SCHEDULED'):
                #job has timed out
                job.state = 'TIMEOUT'
                self.acclient.notifyWorkCompleted(job)

        # self.redisworker.removeJobs(hoursago=2)#@todo does not work

        #@todo more logic required here for old jobs
        

        return result

    def notifyWorkCompleted(self,job):

        w=self.redisworker
        job["timeStop"]=int(time.time())

        if job["jscriptid"]<10000:
            #jumpscripts coming from AC
            if job["state"]<>"OK":
                try:
                    self.acclient.notifyWorkCompleted(job)
                except Exception,e:
                    j.events.opserror("could not report job in error to agentcontroller", category='workers.errorreporting', e=e)
                    return
                #lets keep the errors
                # self.redis.hdel("workers:jobs",job.id)
            else:
                if job["log"]:
                    try:
                        self.acclient.notifyWorkCompleted(job)
                    except Exception,e:
                        j.events.opserror("could not report job result to agentcontroller", category='workers.jobreporting', e=e)
                        return
                    # job.state=="OKR" #means ok reported
                    #we don't have to keep status of local job result, has been forwarded to AC
            self.redisworker.redis.hdel("workers:jobs",job["id"])

    def getJob(self, jobid, session=None):
        """
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  

        return self.redisworker.getJob(jobid)

    def getWorkerStatus(self, session=None):
        """
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd) 
        nid = j.application.whoAmI.nid
        
        result = self.acclient.executeJumpScript('jumpscale', 'workerstatus', nid, timeout=5)
        return result

