from JumpScale import j

class AgentControllerFactory(object):

    def __init__(self):
        self.ipaddr=None
        self.client=None

    def configure(self,agentControllerIP=None):
        """
        @if None will be same as master
        """
        if agentControllerIP==None:
            self.ipaddr=j.application.config.get("grid.master.ip")
        else:
            self.ipaddr=agentControllerIP
        passwd=j.application.config.get("system.superadmin.passwd")
        self.client= j.servers.geventws.getClient(self.ipaddr, 4444, user="admin", passwd=passwd,category="agent")


    def execute(self,organization,name,role,timeout=60,wait=True,lock="",**kwargs):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        if self.client==None:
            self.configure()
        job=client.executeJumpscript(organization,name,role=role,args=kwargs,timeout=timeout,wait=wait,lock=lock)
        return job

    def listJscripts(self):
        """
        return dict with key=scriptname, val=[organization,author, ...]
        """
        #@todo
        if self.client==None:
            self.configure()

    def getJscript(self,scriptOrg,scriptName):
        """
        return dict with all relevant info of jscript (also content)
        """
        #@todo
        if self.client==None:
            self.configure()

    def reloadJscript(self):
        """
        reload jscripts from disk
        """
        #@todo
        if self.client==None:
            self.configure()

    def getJobInfo(self,withLogs=True):
        """
        returh jobobject with all relevant info , also return logs to do with
        @return (jobObject,logTxt)
        logTxt is formatted log (with minimimal relevant content, time not needed, level not needed)
        """
        #@todo
        if self.client==None:
            self.configure()

