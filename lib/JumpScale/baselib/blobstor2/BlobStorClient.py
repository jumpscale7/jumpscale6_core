from JumpScale import j
import lzma
import os
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
        self._MB4=4*1024*1024
        self.compress=True
        self.cachepath=""

    def _normalize(self, path):
        path=path.replace("'","\\'")
        path=path.replace("[","\\[")
        path=path.replace("]","\\]")
        return path

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
        # print "cmd:%s args:%s"%(cmd,args)

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

    def _dump2stor(self, data,key="",repoid=0):
        if len(data)==0:
            return ""
        if key=="":
            key = j.tools.hash.md5_string(data)
        data2 = lzma.compress(data) if self.compress else data
        self.set(key=key, data=data2,repoid=repoid)            
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

    def uploadDir(self,dirpath):
        name="backup_md_%s"%j.base.idgenerator.generateRandomInt(1,100000)
        tarpath="/tmp/%s.tar"%name
        cmd="cd %s;tar cf %s ."%(dirpath,tarpath)
        j.system.process.execute(cmd)
        key=self.uploadFile(tarpath)
        j.system.fs.remove(tarpath)
        return key

    def downloadDir(self,key,dest,repoid=0):
        j.system.fs.removeDirTree(dest)
        j.system.fs.createDir(dest)
        name="backup_md_%s"%j.base.idgenerator.generateRandomInt(1,100000)
        tarpath="/tmp/%s.tar"%name
        self.downloadFile(key,tarpath,False,repoid=repoid)
        cmd="cd %s;tar xf %s"%(dest,tarpath)
        j.system.process.execute(cmd)
        j.system.fs.remove(tarpath)

    def uploadFile(self,path,key="",repoid=0):
        if key=="":
            key=j.tools.hash.md5(path)
        if j.system.fs.statPath(path).st_size>self._MB4:
            print "upload file (>4MB) %s"%(path)
            for data in self._read_file(path):
                hashes.append(self._dump2stor(data,repoid=repoid))
            if len(hashes)>1:
                out = "##HASHLIST##\n"
                hashparts = "\n".join(hashes)
                out += hashparts
                # Store in blobstor
                # out_hash = self._dump2stor(out,key=md5) #hashlist is stored on md5 location of file
                self.set(key=key, data=out,repoid=repoid)   
            else:
                raise RuntimeError("hashist needs to be more than 1.")
        else:
            print "upload file (<4MB) %s"%(path)
            for data in self._read_file(path):
                self._dump2stor(data,key=key,repoid=repoid)
        return key

    def downloadFile(self,key,dest,link=False,repoid=0, chmod=0,chownuid=0,chowngid=0):

        if self.cachepath<>"":
            blob_path = self._getBlobCachePath(key)
            if j.system.fs.exists(blob_path):
                # Blob exists in cache, we can get it from there!
                # print "Blob FOUND in cache: %s" % blob_path
                if link:
                    self._link(blob_path,dest)
                else:
                    j.system.fs.copyFile(blob_path, dest)
                return

        # Get blob from blobstor2
        blob = self.get( key,repoid=repoid)

        if blob==None:
            raise RuntimeError("Cannot find blob with key:%s"%key)
        
        
        if self.cachepath<>"":
            self._restoreBlobToDest(blob_path, blob, chmod=chmod,chownuid=chownuid,chowngid=chowngid)
            j.system.fs.createDir(j.system.fs.getDirName(dest))
            if link:
                self._link(blob_path,dest)
            else:
                j.system.fs.copyFile(blob_path, dest)            
        else:
            self._restoreBlobToDest(dest, blob, chmod=chmod,chownuid=chownuid,chowngid=chowngid)

    def _getBlobCachePath(self, key):
        """
        Get the blob path in Cache dir
        """
        # Get the Intermediate path of a certain blob
        storpath = j.system.fs.joinPaths(self.cachepath, key[0:2], key[2:4], key)
        return storpath


    def _restoreBlobToDest(self, dest, blob, chmod=0,chownuid=0,chowngid=0):
        """
        Write blob to destination
        """
        check="##HASHLIST##"
        j.system.fs.createDir(j.system.fs.getDirName(dest))
        if blob.find(check)==0:
            # found hashlist
            # print "FOUND HASHLIST %s" % blob
            hashlist = blob[len(check) + 1:]            
            j.system.fs.writeFile(dest,"")
            for hashitem in hashlist.split("\n"):
                if hashitem.strip() != "":
                    blob_block = self.get(hashitem)
                    if self.compress:
                        blob_block = lzma.decompress(blob_block)
                    j.system.fs.writeFile(dest, blob_block, append=True)
        else:
            # content is there
            if self.compress:
                blob = lzma.decompress(blob)
            j.system.fs.writeFile(dest, blob)

        # chmod/chown
        if chmod<>0:
            os.chmod(dest,chmod)
        if chownuid<>0:
            os.chown(dest,chownuid,chowngid)       

    def _link(self, src, dest):

        j.system.fs.createDir(j.system.fs.getDirName(dest))
        # print "link:%s %s"%(src, dest)

        if j.system.fs.exists(path=dest):
            stat=j.system.fs.statPath(dest)
            if stat.st_nlink<2:
                raise RuntimeError("only support linked files")
        else:
            cmd="ln '%s' '%s'"%(self._normalize(src),self._normalize(dest))
            try:
                j.system.process.execute(cmd)
            except Exception,e:
                print "ERROR LINK FILE",
                print cmd
                print e
                self.errors.append(["link",cmd,e])
