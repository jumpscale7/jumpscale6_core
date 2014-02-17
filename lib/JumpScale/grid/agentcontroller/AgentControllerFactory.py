from JumpScale import j
import ujson

class AgentControllerFactory(object):

    def get(self,agentControllerIP=None):
        """
        @if None will be same as master
        """
        return AgentControllerClient(agentControllerIP)

class AgentControllerClient():
    def __init__(self,agentControllerIP):
        import JumpScale.grid.geventws
        if agentControllerIP==None:
            self.ipaddr=j.application.config.get("grid.master.ip")
        else:
            self.ipaddr=agentControllerIP
        passwd=j.application.config.get("grid.master.superadminpasswd")
        login=j.application.config.get("system.superadmin.login")
        client= j.servers.geventws.getClient(self.ipaddr, 4444, user=login, passwd=passwd,category="agent")
        self.__dict__.update(client.__dict__)

    def execute(self,organization,name,role,timeout=60,wait=True,queue="",dieOnFailure=True,**kwargs):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        job = self.executeJumpScript(organization,name,role=role,args=kwargs,timeout=timeout,wait=wait,queue=queue,transporttimeout=timeout)
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
