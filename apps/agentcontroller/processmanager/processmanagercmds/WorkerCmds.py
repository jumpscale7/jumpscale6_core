from JumpScale import j
import time

class WorkerCmds():

    def __init__(self,daemon=None):
        self._name="worker"
        if not daemon:
            return
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth

    def getQueuedJobs(self,format="json",session=None):        
        """
        @format can be json or wiki
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class see getQueuedJobs
        #only use local redis on port 6678
        
    def getFailedJobs(self,format="json",session=None):
        """
        @format can be json or wiki
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class make new method
        #only use local redis on port 6678

    def getJob(self,session=None):        
        """
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)  
        # use complement RedisWorkerFactory class make new method
        #only use local redis on port 6678

