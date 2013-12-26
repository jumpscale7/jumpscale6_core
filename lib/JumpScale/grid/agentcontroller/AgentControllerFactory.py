from JumpScale import j
import ujson

class AgentControllerFactory(object):

    def __init__(self):
        self.ipaddr=None
        self._client=None

    def configure(self,agentControllerIP=None):
        """
        @if None will be same as master
        """
        import JumpScale.grid.geventws
        if agentControllerIP==None:
            self.ipaddr=j.application.config.get("grid.master.ip")
        else:
            self.ipaddr=agentControllerIP
        passwd=j.application.config.get("system.superadmin.passwd")
        login=j.application.config.get("system.superadmin.login")
        self._client= j.servers.geventws.getClient(self.ipaddr, 4444, user=login, passwd=passwd,category="agent")

    @property
    def client(self):
        if not self._client:
            self.configure()
        return self._client

    def execute(self,organization,name,role,timeout=60,wait=True,lock="",dieOnFailure=True,**kwargs):
        return self.executeKwargs(organization, name, role, timeout, wait, lock, dieOnFailure, kwargs)

    def executeKwargs(self,organization,name,role,timeout=60,wait=True,lock="",dieOnFailure=True,kwargs=None):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        kwargs = kwargs or dict()
        job= self.client.executeJumpscript(organization,name,role=role,args=kwargs,timeout=timeout,wait=wait,lock=lock,transporttimeout=timeout)
        if job["state"]=="ERROR":
            eco=j.errorconditionhandler.getErrorConditionObject(ujson.loads(job["result"]))
            print eco
            if dieOnFailure:
                raise RuntimeError("Could not execute %s %s for role:%s, jobid was:%s"%(organization,name,role,job["id"]))
                #j.errorconditionhandler.processErrorConditionObject(eco)

        if wait:
            if job["result"]==None:
                return None
            else:
                return ujson.loads(job["result"])
        else:
            return job
            
        

    def listJumpScripts(self, organization=None, cat=None):
        """
        return dict with key=scriptname, val=[organization,author, ...]
        """
        return self.client.listJumpScripts(organization, cat)

    def getJumpScript(self,organization,name):
        """
        return dict with all relevant info of jscript (also content)
        """
        return self.client.getJumpScript(organization, name)

    def reloadJscript(self):
        """
        reload jscripts from disk
        """
        return self.client.loadJumpscripts()

    def getJobInfo(self, jobid, withLogs=True):
        """
        returh jobobject with all relevant info , also return logs to do with
        @return (jobObject,logTxt)
        logTxt is formatted log (with minimimal relevant content, time not needed, level not needed)
        """
        return self.client.getJobInfo(jobid)

    def listSessions(self):
        return self.client.listSessions()

    def getActiveJobs(self):
        return self.client.getActiveJobs()

