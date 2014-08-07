from JumpScale import j
import ujson as json

PORT = 4444

class AgentControllerFactory(object):
    def __init__(self):
        self._agentControllerClients={}
        self._agentControllerProxyClients={}

    def get(self,agentControllerIP=None, port=PORT):
        """
        @if None will be same as master
        """
        connection = (agentControllerIP, port)
        if connection not in self._agentControllerClients:
            self._agentControllerClients[connection]=AgentControllerClient(agentControllerIP, port)
        return self._agentControllerClients[connection]

    def getInstanceConfig(self, instance):
        accljp = j.packages.findNewest(name="agentcontroller_client",domain="jumpscale")
        accljp = accljp.getInstance(instance)
        hrd = accljp.hrd_instance
        ipaddr = hrd.get("agentcontroller.client.addr")
        port = int(hrd.get("agentcontroller.client.port"))
        return ipaddr, port

    def getByInstance(self, instance):
        ipaddr, port = self.getInstanceConfig(instance)
        return self.get(ipaddr, port)

    def getClientProxy(self,category="jpackages",agentControllerIP=None):
        key="%s_%s"%(category,agentControllerIP)
        if not self._agentControllerProxyClients.has_key(key):
            self._agentControllerProxyClients[key]=AgentControllerProxyClient(category,agentControllerIP)
        return self._agentControllerProxyClients[key]        

class AgentControllerProxyClient():
    def __init__(self,category,agentControllerIP):
        self.category=category
        import JumpScale.grid.geventws
        if agentControllerIP==None:
            acipkey = "grid.agentcontroller.ip"
            if j.application.config.exists(acipkey):
                self.ipaddr=j.application.config.get(acipkey)
            else:
                self.ipaddr=j.application.config.get("grid.master.ip")
        else:
            self.ipaddr=agentControllerIP
        passwd=j.application.config.get("grid.master.superadminpasswd")
        login=j.application.config.get("system.superadmin.login")
        client= j.servers.geventws.getClient(self.ipaddr, PORT, user=login, passwd=passwd,category="processmanager_%s"%category)
        self.__dict__.update(client.__dict__)

class AgentControllerClient():
    def __init__(self,agentControllerIP, port=PORT):
        import JumpScale.grid.geventws

        if agentControllerIP:
            self.ipaddr = agentControllerIP
            connections = [ (agentControllerIP, port) ]
        elif j.application.config.exists('grid.agentcontroller.ip'):
            connections = [ (ip, port) for ip in j.application.config.getList('grid.agentcontroller.ip') ]
        else:
            connections = [ (j.application.config.get("grid.master.ip"), port) ]
        passwd=j.application.config.get("grid.master.superadminpasswd")
        login=j.application.config.get("system.superadmin.login")
        client= j.servers.geventws.getHAClient(connections, user=login, passwd=passwd,category="agent")
        self.__dict__.update(client.__dict__)


    def execute(self,organization,name,role=None,nid=None,timeout=60,wait=True,queue="",dieOnFailure=True,errorreport=True,**kwargs):
        """
        the arguments just put at end like executeWait("test",myarg=111,something=222)
        """
        errorReportOnServer=errorreport
        if wait==True:
            errorReportOnServer=False
        result = self.executeJumpScript(organization,name,nid=nid,role=role,args=kwargs,timeout=timeout,\
            wait=wait,queue=queue,transporttimeout=timeout,errorreport=errorReportOnServer)
        if wait and result['state'] != 'OK':
            if result['state'] == 'NOWORK' and dieOnFailure:
                raise RuntimeError('Could not find agent with role:%s' %  role)
            if result['result']<>"":
                ecodict=json.loads(result['result'])
                eco=j.errorconditionhandler.getErrorConditionObject(ddict=ecodict)
                # eco.gid=result["gid"]
                # eco.nid=result["nid"]
                # eco.jid=result["id"]

                if errorreport:
                    j.errorconditionhandler.processErrorConditionObject(eco,tostdout=False,sentry=True,\
                        modulename="agent", centralsentry=True)
                
                msg="%s\n\nCould not execute %s %s for role:%s, jobid was:%s\n"%(eco,organization,name,role,result["id"])

                if errorreport:
                    print msg                     

                if dieOnFailure:  
                    j.errorconditionhandler.halt(msg)
                
        if wait:
            return result["result"]
        else:
            return result
