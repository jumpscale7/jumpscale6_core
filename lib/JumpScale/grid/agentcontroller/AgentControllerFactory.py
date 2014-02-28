from JumpScale import j
import ujson

class AgentControllerFactory(object):
    def __init__(self):
        self.agentControllerClients={}
        self.agentControllerProxyClients={}

    def get(self,agentControllerIP=None):
        """
        @if None will be same as master
        """
        if not self.agentControllerClients.has_key(agentControllerIP):
            self.agentControllerClients[agentControllerIP]=AgentControllerClient(agentControllerIP)
        return self.agentControllerClients[agentControllerIP]
        
    def getClientProxy(self,category="jpackages",agentControllerIP=None):
        key="%s_%s"%(category,agentControllerIP)
        if not self.agentControllerProxyClients.has_key(key):
            self.agentControllerProxyClients[key]=AgentControllerProxyClient(category,agentControllerIP)
        return self.agentControllerProxyClients[key]        

class AgentControllerProxyClient():
    def __init__(self,category,agentControllerIP):
        self.category=category
        import JumpScale.grid.geventws
        if agentControllerIP==None:
            self.ipaddr=j.application.config.get("grid.master.ip")
        else:
            self.ipaddr=agentControllerIP
        passwd=j.application.config.get("grid.master.superadminpasswd")
        login=j.application.config.get("system.superadmin.login")
        client= j.servers.geventws.getClient(self.ipaddr, 4444, user=login, passwd=passwd,category="processmanager_%s"%category)
        self.__dict__.update(client.__dict__)

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


    def execute(self,organization,name,role=None,nid=None,timeout=60,wait=True,queue="",dieOnFailure=True,**kwargs):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        result = self.executeJumpScript(organization,name,role=role,args=kwargs,timeout=timeout,wait=wait,queue=queue,transporttimeout=timeout)
        if wait and result['state'] != 'OK':
            if result['state'] == 'NOWORK' and dieOnFailure:
                raise RuntimeError('Could not find agent with role:%s' %  role)
            if result['result']:
                if dieOnFailure:
                    raise RuntimeError("Could not execute %s %s for role:%s, jobid was:%s error: %s"%(organization,name,role,result["id"], result['result']))
                #j.errorconditionhandler.processErrorConditionObject(eco)
        if wait:
            return result["result"]
        else:
            return result
