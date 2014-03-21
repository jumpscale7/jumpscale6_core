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
            self.queue=[]
            self.queuedatasize=0
            return res

    def set(self,key, data,repoid=0,sendnow=True,sync=True,timeout=60):
        """
        """
        return self._execCmd("SET",{"key":key,"namespace":self.namespace,"repoid":repoid},data=data,sendnow=sendnow,sync=sync,timeout=timeout)        

    def sync(self):
        """
        """
        return self._execCmd("SYNC",{"namespace":self.namespace},data="",sendnow=True,sync=True,timeout=2)        


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
        return self._execCmd("EXISTS",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=2)

    def getMD(self,key):
        return self._execCmd("GETMD",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=2) 

    def delete(self,key, repoid=0,force=False):
        return self._execCmd("DELETE",{"key":key,"namespace":self.namespace,"repoid":repoid},sendnow=True,sync=True,timeout=60)

    def deleteNamespace(self):
        return self._execCmd("DELNS",{"namespace":self.namespace},sendnow=True,sync=True,timeout=600) 

    def _dump2stor(self, data,key=""):
        if len(data)==0:
            return ""
        if key=="":
            key = j.tools.hash.md5_string(data)
        data2 = lzma.compress(data) if self.compress else data
        self.set(key=key, data=data2,repoid=self.repoId)            
        return key

    def _read_file(self,path, block_size=0):
        if block_size==0:
            block_size=self._MB4

        with open(path, 'rb') as f:
            while True:
                piece = f.read(block_size)
                if piece:
                    yield piece
                else:
                    return

    def uploadDirTAR(self,dirpath):
        name="backup_md_%s"%j.base.idgenerator.generateRandomInt(1,100000)
        cmd="cd %s;tar czvfh /tmp/%s.tar.gz"%(dirpath,name)
        j.system.process.execute(cmd)
        # j.sysm.fs.remove("/tmp/%s.tar.gz"%name)
        from IPython import embed
        print "DEBUG NOW uploadDirTAR"
        embed()

    def uploadFile(self,path):
        pass
        
