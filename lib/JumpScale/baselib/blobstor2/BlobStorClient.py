from JumpScale import j

import ujson
# import 

class BlobStorClient:
    """
    client to blobstormaster
    """

    def __init__(self, master,domain,namespace):        
        self.master=master
        self.domain=domain
        self.namespace=namespace
        self.setGetNamespace()
        self.rmsize=len(self.nsobj["routeMap"])
        self.queue=[]
        self.queuedatasize=0
        self.maxqueuedatasize=1*1024*1024 #1MB

    def setGetNamespace(self,nsobj=None):
        if nsobj==None:            
            ns=self.master.getNamespace(domain=self.domain,name=self.namespace)
            if ns==None:            
                ns=self.master.newNamespace(domain=self.domain,name=self.namespace)        
        else:
            ns=self.master.setNamespace(namespaceobject=nsobj.__dict__)
        self.nsobj=ns
        self.replicaMaxSize=self.nsobj["replicaMaxSizeKB"]*1024
        self.nsid=self.nsobj["id"]
        return ns

    def _getBlobStorConnection(self,datasize=0,random=False):
        return j.clients.blobstor2.getBlobStorConnection(self.master,self.nsobj,datasize,random=random)

    def _execCmd(self,cmd="",args={},data="",sendnow=True,sync=True,timeout=60):

        self.queue.append((cmd,args,data))
        self.queuedatasize+=len(data)
    
        if sendnow or len(self.queue)>100 or self.queuedatasize>self.maxqueuedatasize:
            c=self._getBlobStorConnection(datasize=self.queuedatasize)
            res=c.sendCmds(self.queue,sync=sync,timeout=timeout)
            print "send"
            self.queue=[]
            self.queuedatasize=0
            return res


    def set(self,key, data,repoid=0,sendnow=True,sync=True,timeout=60):
        """
        """
        return self._execCmd("SET",{"key":key,"namespace":self.namespace,"repoid":repoid},data=data,sendnow=sendnow,sync=sync,timeout=timeout)        

    def get(self, key,repoid=0,timeout=60):
        """
        get the block back
        """
        return self._execCmd("GET",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=timeout)  

    def existsBatch(self,keys,repoid=0,replicaCheck=False):
        c=self._getBlobStorConnection()
        return self._execCmd("EXISTSBATCH",{"keys":keys,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=600) 

    def exists(self,key,repoid=0,replicaCheck=False):
        """
        Checks if the blobstor contains an entry for the given key
        @param key: key to Check
        @replicaCheck if True will check that there are enough replicas (not implemented)
        the normal check is just against the metadata stor on the server, so can be data is lost
        """
        return self.get( key,repoid=repoid,timeout=60)<>None

    def getMD(self,key):
        return self._execCmd("GETMD",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=2) 

    def delete(self,key, repoid=0,force=False):
        return self._execCmd("DELETE",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=60)

    def deleteNamespace(self):
        return self._execCmd("DELNS",{"namespace":self.namespace},sendnow=True,sync=True,timeout=600) 

