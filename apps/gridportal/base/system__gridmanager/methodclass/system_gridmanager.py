from JumpScale import j
import JumpScale.grid.geventws
import JumpScale.grid.osis
import JumpScale.grid.agentcontroller
import requests

class system_gridmanager(j.code.classGetBase()):
    """
    gateway to grid
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="gridmanager"
        self.appname="system"
        self.clients={}
        self._nodeMap = dict()
        self.clientsIp = dict()

        self.passwd = j.application.config.get("system.superadmin.passwd")

        osis = j.core.osis.getClient(j.application.config.get("grid.master.ip"), passwd=self.passwd)
        self.osis_node = j.core.osis.getClientForCategory(osis,"system","node")

    def getClient(self,nid):
        nid = int(nid)
        if nid not in self.clients:
            if nid not in self._nodeMap:
                try:
                    self._getNode(nid)
                except:
                    pass # if node not found next line will crash
            if nid not in self._nodeMap:
                raise RuntimeError('Could not get client for node %s!' % nid)
            for ip in self._nodeMap[nid]['ipaddr']:
                if j.system.net.tcpPortConnectionTest(ip, 4445):
                    self.clients[nid] = j.servers.geventws.getClient(ip, 4445, org="myorg", user="admin", passwd="1234",category="processmanager")
                    self.clientsIp[nid] = ip
                    return self.clients[nid]

        return self.clients[nid]

    def getNodeSystemStats(self, nodeId, **kwargs):
        """
        ask the right processmanager on right node to get the information about node system
        param:nodeId id of node
        result json
        """
        client=self.getClient(nodeId)
        return client.monitorSystem()

    def _getNode(self, nid):
        node=self.osis_node.get(nid)
        r = dict()
        r["id"]=node.id
        r["roles"]=node.roles
        r["name"]=node.name
        r["ipaddr"]=node.ipaddr
        self._nodeMap[nid] = r
        return r

    def getNodes(self, **kwargs):
        """
        list found nodes
        result list(list)
        """
        result=[]
        for nid in self.osis_node.list():
            node = self._getNode(nid)
            result.append(node)
        return result

    def getProcessStats(self, nodeId, domain="", name="", **kwargs):
        """
        ask the right processmanager on right node to get the information
        param:nodeId id of node
        param:domain optional domain name for process
        param:name optional name for process
        result json
        """
        if domain=="*":
            domain=""
        if name=="*":
            name=""
        client=self.getClient(nodeId)
        return client.monitorProcess(domain=domain,name=name)

    def getStat(self,statKey,width=500,height=250, **kwargs):
        """
        @param statkey e.g. n1.disk.mbytes.read.sda1.last
        """
        statKey=statKey.strip()
        if statKey[0]=="n":
            #node info
            nodeId=int(statKey.split(".")[0].replace("n",""))
        else:
            raise RuntimeError("Could not parse statKey, only node stats supported for now (means starting with n)")

        client=self.getClient(nodeId)
        ip=self.clientsIp[nodeId] 

        url="http://%s:8081/render/?width=%s&height=%s&target=%s&lineWidth=2&graphOnly=false&hideAxes=false&hideGrid=false&areaMode=first&tz=CET"%(ip,width,height,statKey)

        r = requests.get(url)

        return r.content

    def getProcessesActive(self, nodeId, name, domain, **kwargs):
        """
        ask the right processmanager on right node to get the info (this comes not from osis)
        output all relevant info (no stat info for that we have getProcessStats)
        param:nodeId id of node (if not specified goes to all nodes and aggregates)
        param:name optional name for process name (part of process name)
        param:domain optional name for process domain (part of process domain)
        result json 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getProcessesActive")

    def getJob(self, id, includeloginfo, includechildren, **kwargs):
        """
        gets relevant info of job (also logs)
        can be used toreal time return job info
        param:id obliged id of job
        param:includeloginfo if true fetch all logs of job & return as well
        param:includechildren if true look for jobs which are children & return that info as well
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJob")

    def getStatImage(self, statKey, width, height, **kwargs):
        """
        get png image as binary format
        comes from right processmanager
        param:statKey e.g. n1.disk.mbytes.read.sda1.last
        param:width 
        param:height 
        result binary 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getStatImage")

    def getLogs(self, id, level, category, text, from_, to, jid, nid, gid, pid, tags, **kwargs):
        """
        interface to get log information
        param:id only find 1 log entry
        param:level level between 1 & 9; all levels underneath are found e.g. level 9 means all levels
        param:category match on multiple categories; are comma separated
        param:text match on text in body
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find logs to date specified
        param:jid find logs for specified jobid
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:pid find logs for specified process (on grid level)
        param:tags comma separted list of tags/labels
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getLogs")

    def getJobs(self, id, from_, to, nid, gid, parent, roles, state, jsorganization, jsname, **kwargs):
        """
        interface to get job information
        param:id only find 1 job entry
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find jobs to date specified
        param:nid find jobs for specified node
        param:gid find jobs for specified grid
        param:parent find jobs which are children of specified parent
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:state OK;ERROR;...
        param:jsorganization 
        param:jsname 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJobs")

    def getErrorconditions(self, id, level, descr, descrpub, from_, to, nid, gid, category, tags, type, jid, jidparent, jsorganization, jsname, **kwargs):
        """
        interface to get errorcondition information (eco)
        param:id only find 1 eco entry
        param:level level between 1 & 3; all levels underneath are found e.g. level 3 means all levels
        param:descr match on text in descr
        param:descrpub match on text in descrpub
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find ecos to date specified
        param:nid find ecos for specified node
        param:gid find ecos for specified grid
        param:category match on multiple categories; are comma separated
        param:tags comma separted list of tags/labels
        param:type 
        param:jid find ecos for specified job
        param:jidparent find ecos which are children of specified parent job
        param:jsorganization find ecos coming from scripts from this org
        param:jsname find ecos coming from scripts with this name
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getErrorconditions")

    def getProcesses(self, id, name, nid, gid, aid, from_, to, **kwargs):
        """
        list processes (comes from osis), are the grid unique processes (not integrated with processmanager yet)
        param:id only find 1 process entry
        param:name match on text in name
        param:nid find logs for specified node
        param:gid find logs for specified grid
        param:aid find logs for specified application type
        param:from_ -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes from date specified  (-4d means 4 days ago)
        param:to -4d;-4w;-4m;-1h;-1s  d=day w=week m=month s=sec  find processes to date specified
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getProcesses")

    def getApplications(self, id, type, descr, **kwargs):
        """
        list known application types (applicationtype in osis)
        param:id only find 1 process entry
        param:type 
        param:descr match on text in descr
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getApplications")

    def getGrids(self, **kwargs):
        """
        list grids
        result list(list) 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getGrids")

    def getJumpscript(self, jsorganization, jsname, **kwargs):
        """
        calls internally the agentcontroller to fetch detail for 1 jumpscript
        param:jsorganization 
        param:jsname 
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJumpscript")
 
    def getJumpscripts(self, jsorganization, **kwargs):
        """
        calls internally the agentcontroller
        return: lists the jumpscripts with main fields (organization, name, category, descr)
        param:jsorganization find jumpscripts
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getJumpscripts")
    
    def getAgentControllerActiveJobs(self, **kwargs):
        """
        calls internally the agentcontroller
        list jobs now running on agentcontroller
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAgentControllerActiveJobs")
    

    def getAgentControllerSessions(self, roles, nid, active, **kwargs):
        """
        calls internally the agentcontroller
        param:roles match on comma separated list of roles (subsets also ok e.g. kvm.  would match all roles starting with kvm.)
        param:nid find for specified node (on which agents are running which have sessions with the agentcontroller)
        param:active is session active or not
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAgentControllerSessions")
