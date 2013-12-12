from JumpScale import j

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


    def execute(self,organization,name,role,timeout=60,wait=True,lock="",**kwargs):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        return self.client.executeJumpscript(organization,name,role=role,args=kwargs,timeout=timeout,wait=wait,lock=lock)

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

