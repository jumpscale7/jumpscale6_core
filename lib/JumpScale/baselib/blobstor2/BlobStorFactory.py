from JumpScale import j

from BlobStorClient import *
from BlobStorServer import *
from BlobStorMaster import *
from BlobStorWorker import *

import JumpScale.baselib.credis

# import msgpack

# _pack_pipeline_command

import JumpScale.grid.zdaemon

BSTRANSPPARENT=j.core.zdaemon.getZDaemonTransportClass()
class BlobStorTransport(BSTRANSPPARENT):

    def __init__(self,addr,port,gevent=True):
        BSTRANSPPARENT.__init__(self,addr=addr,port=port,gevent=gevent)
        self._init()
        # self.redis=j.clients.blobstor2.redis.redis
        self.packcmds=j.clients.blobstor2.redis.redis.pack_pipeline_command_list

    def sendCmds(self,cmds,transaction=True):
        """
        list of cmds, each cmd is a tuple which can be understood by redis
        """
        if transaction and len(cmds)>0:
            cmds.insert(0,("MULTI",))
            cmds.append(("EXEC",))
            
        args=self.packcmds(cmds)

        self._cmdchannel.send_multipart(args)
        result=self._cmdchannel.recv_multipart()

        
        if result[0]=="DENY":
            raise RuntimeError("cmds could not be send, access denied.")
        else:
            return result

    def queueCMD(self,cmd,key,data="",subkey="",sendnow=False):
        if data=="":
            self.queue.append((cmd,key))
        else:
            if subkey=="":
                self.queue.append((cmd,key,data))
            else:
                self.queue.append((cmd,key,subkey,data))
            self.queuedatasize+=len(data)
        if sendnow or len(self.queue)>100 or self.queuedatasize>self.maxqueuedatasize:
            self.sendNow()

    def sendNow(self):
        c=self._getBlobStorConnection(datasize=self.queuedatasize)
        res=c.sendCmds(self.queue,transaction=True)
        self.queue=[]
        self.queuedatasize=0
        return res            


class BlobStorFactory:
    def __init__(self):
        self.logenable=True
        self.loglevel=5
        self._blobstorMasterCache={}
        self._blobstorCache={}
        self.redis = j.clients.credis.getRedisClient("127.0.0.1", 7767,timeout=2)
        self.nodes={}
        self.disks={}
        self.replicaMaxSize=256*1024

    def getClient(self, name,domain,namespace):
        return BlobStorClient(self.getMasterClient(name=name),domain,namespace)

    def getMasterClient(self,name="default"):
        id=0
        for key in j.application.config.getKeysFromPrefix("blobclient.blobserver"):
            # key=key.replace("gitlabclient.server.","")
            if key.find("name")<>-1:
                if j.application.config.get(key)==name:
                    key2=key.replace("blobclient.blobserver.","")
                    id=key2.split(".")[0]
        if id==0:
            raise RuntimeError("Did not find account:%s for blobserverclient")
        prefix="blobclient.blobserver.%s"%id
        ipaddr=j.application.config.get("%s.addr"%prefix)
        port=j.application.config.get("%s.port"%prefix)
        login=j.application.config.get("%s.login"%prefix)
        passwd=j.application.config.get("%s.passwd"%prefix)
        
        name="%s_%s"%(ipaddr,port)
        if self._blobstorMasterCache.has_key(name):
            return self._blobstorMasterCache[name]        
        self._blobstorMasterCache[name]= j.servers.zdaemon.getZDaemonClient(addr=ipaddr,port=port,user=login,passwd=passwd,ssl=False,sendformat='m', returnformat='m',category="blobstormaster")
        return self._blobstorMasterCache[name]        

    def getBlobStorConnection(self,master,nsobj,datasize=0,random=False):
        rmsize=len(nsobj["routeMap"])
        if random or datasize>self.replicaMaxSize:
            #spread data
            i=j.base.idgenerator.generateRandomInt(0,rmsize-1)
            bsnodeid=nsobj["routeMap"][i]
        else:
            #replicate
            rmsize=min([rmsize,3]) #first 3 nodes or less if not available
            i=j.base.idgenerator.generateRandomInt(0,rmsize-1) #the ones with most free space are used
            bsnodeid=nsobj["routeMap"][i]            

        if self._blobstorCache.has_key(bsnodeid):
            return self._blobstorCache[bsnodeid]
        ipaddr, port,key=master.getNodeLoginDetails(bsnodeid)        
        self._blobstorCache[bsnodeid]=  BlobStorTransport(addr=ipaddr,port=port,gevent=True)

        return self._blobstorCache[bsnodeid]

    def _getNodesDisks(self):
        rkey="blobstormaster:nodes"
        result=None
        if self.redis.exists(rkey):
            try:
                result=self.redis.get(rkey)
            except Exception,e:
                #means in just this time it expired
                pass
            result=ujson.loads(result)
            self.nodes=result[0]
            self.disks=result[1]
        return result

    def _setNodesDisks(self):
        rkey="blobstormaster:nodes"
        todelete=[]
        for key,obj in self.nodes.iteritems():
            if obj["size"]<obj["free"]:
                obj["free"]=obj["size"]
            if obj["free"]==0:
                todelete.append(key)
        for key in todelete:                
            self.nodes.pop(key)
        self.redis.set(rkey,ujson.dumps([self.nodes,self.disks]))
        self.redis.expire(rkey,60)

    def _getNS(self,domain,name):
        rkey="blobstormaster:ns:%s_%s"%(domain,name)
        if self.redis.exists(rkey):
            try:
                result=self.redis.get(rkey)
            except Exception,e:
                #means in just this time it expired
                return None
            ns=ujson.loads(result)
            return ns
        return None

    def _setNS(self,ns):
        rkey="blobstormaster:ns:%s_%s"%(ns["domain"],ns["name"])
        self.redis.set(rkey,ujson.dumps(ns))
        self.redis.expire(rkey,3600)

    def getNodesDisks(self):
        if self._getNodesDisks()==None: #check if already in redis
            self.master.getNodesDisks() #get from master (which gets it from osis)
            self._setNodesDisks() #put to redis
        return (self.nodes,self.disks)

    def getNamespace(self,domain,name):
        ns=self._getNS(domain, name)
        if ns<>None:
            return ns
        else:
            ns=self.master.getNamespace(domain,name)
            self._setNS(ns)

    def log(self,msg,category="",level=5):
        if level<self.loglevel+1 and self.logenable:
            j.logger.log(msg,category="blobstor.%s"%category,level=level)

class BlobStorFactoryServer:

    def start(self,port=2345):
        bss=BlobStorServer(port=port)
        bss.start()

    def startMaster(self,port=2344):
        bsm=BlobStorMaster(port=port)
        bsm.start()

    def startWorker(self,path):
        bsw=BlobStorWorker(path=path)
        bsw.start()
