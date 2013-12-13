from JumpScale import j
import JumpScale.grid.geventws
import JumpScale.grid.osis
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
        self.clientsIp={}

        self.passwd=passwd=j.application.config.get("system.superadmin.passwd")

        osis=j.core.osis.getClient(j.application.config.get("grid.master.ip"),passwd=self.passwd)
        self.osis_node=j.core.osis.getClientForCategory(osis,"system","node")

    def getClient(self,nid):
        if not self.clients.has_key(nid):
            for node in self.getNodes():                
                if str(node["id"])==str(nid):
                    for ip in node["ipaddr"]:
                        print "test:%s"%ip
                        if j.system.net.tcpPortConnectionTest(ip,4445):
                            self.clients[nid] = j.servers.geventws.getClient(ip, 4445, org="myorg", user="admin", passwd="1234",category="processmanager")
                            self.clientsIp[nid] = ip
                            return self.clients[nid]  
                
        if not self.clients.has_key(nid):
            raise RuntimeError("Could not find reachable process manager on node %s"%nid)

        return self.clients[nid]
    

    def getNodeSystemStats(self, nodeId, **kwargs):
        """
        ask the right processmanager on right node to get the information about node system
        param:nodeId id of node
        result json 
        
        """
        client=self.getClient(nodeId)
        return client.monitorSystem()
    

    def getNodes(self, **kwargs):
        """
        list found nodes
        result list(list) 
        
        """
        result=[]
        for nodeid in self.osis_node.list():
            node=self.osis_node.get(nodeid)
            r={}
            r["id"]=node.id
            r["roles"]=node.roles
            r["name"]=node.name
            r["ipaddr"]=node.ipaddr
            result.append(r)
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
