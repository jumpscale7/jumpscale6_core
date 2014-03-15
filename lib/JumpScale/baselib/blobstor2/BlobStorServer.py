from JumpScale import j

import time

import JumpScale.baselib.credis

from JumpScale import j
# import JumpScale.grid
# import zmq
import gevent
import gevent.monkey
import zmq.green as zmq
import time
import tarfile
import StringIO

GeventLoop = j.core.gevent.getGeventLoopClass()

class BlobStorServer(GeventLoop):

    def __init__(self, port=2345,path="/mnt/BLOBSTOR", nrCmdGreenlets=50):

        j.application.initGrid()

        self.path=path
        
        j.application.initGrid()

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"

        #check redis is there if not try to start
        if not j.system.net.tcpPortConnectionTest("127.0.0.1",7767):
            j.packages.findNewest(name="redis").install()
            j.packages.findNewest(name="redis").start()

        def checkblobstormaster():
            masterip=j.application.config.get("grid.master.ip")
            self.master=j.servers.zdaemon.getZDaemonClient(
                masterip,
                port=2344,
                user=self.adminuser,
                passwd=self.adminpasswd,
                ssl=False, sendformat='m', returnformat='m', category="blobstormaster")

        success=False
        while success==False:
            try:
                print "connect to blobstormaster"
                checkblobstormaster()
                success=True
            except Exception,e:
                masterip=j.application.config.get("grid.master.ip")
                msg="Cannot connect to blobstormaster %s, will retry in 60 sec."%(masterip)
                j.events.opserror(msg, category='blobstorworker.startup', e=e)
                time.sleep(60)

        #registration of node & disk

        C="""
blobstor.disk.id=0
blobstor.disk.size=100
""" 
        bsnid=self.master.registerNode(j.application.whoAmI.nid)
        nid=j.application.whoAmI.nid
        for item in j.system.fs.listDirsInDir(self.path, recursive=False, dirNameOnly=False, findDirectorySymlinks=True):
            cfigpath=j.system.fs.joinPaths(item,"main.hrd")
            if not j.system.fs.exists(path=cfigpath):
                j.system.fs.writeFile(filename=cfigpath,contents=C)
            hrd=j.core.hrd.getHRD(path=cfigpath)
            if hrd.get("blobstor.disk.id")=="0":
                sizeGB=j.console.askInteger("please give datasize (GB) for this blobstor mount path:%s"%item)
                diskid=self.master.registerDisk(nid=nid,bsnodeid=bsnid, path=item, sizeGB=sizeGB)
                hrd.set("blobstor.disk.id",diskid)
                hrd.set("blobstor.disk.size",sizeGB)


        gevent.monkey.patch_socket()
        GeventLoop.__init__(self)

        self.port = port
        self.nrCmdGreenlets = nrCmdGreenlets

        self.redis=j.clients.blobstor2.redis.redis

        self.disks=[]
        self.diskid2path={}
        self.cidMax={}
        self.nrdisks=0
        self.activeContainer=None
        self.activeContainerNrFilesAdded=0
        self.activeContainerSize=0
        self.activeContainerMaxSize=15*1024*1024
        self.diskfreeMinSize=200*1024*1024

    def monitorDisks(self):
        for item in j.system.fs.listDirsInDir(self.path, recursive=False, dirNameOnly=False, findDirectorySymlinks=True):
            cfigpath=j.system.fs.joinPaths(item,"main.hrd")
            if not j.system.fs.exists(path=cfigpath):
                raise RuntimeError("there should be main.hrd file.")
            hrd=j.core.hrd.getHRD(path=cfigpath)
            if hrd.get("blobstor.disk.id")=="0":
                raise RuntimeError("cfg file on %s not filled in properly"%cfigpath)
            else:
                self.disks=[]
                size=hrd.getInt("blobstor.disk.size")
                diskid=hrd.getInt("blobstor.disk.id")
                diskpath=item
                diskfree=100 #@todo need to implement
                diskid=self.master.registerDisk(nid=nid,bsnodeid=bsnid, path=item, sizeGB=size, diskId=diskid)
                self.disks.append((diskid,diskpath,diskfree))
                self.diskid2path[diskid]=diskpath
                self.nrdisks+=1
                hlids=[int(item) for item in j.system.fs.listDirsInDir(diskpath, recursive=False, dirNameOnly=True, findDirectorySymlinks=True)]
                if hlids=[]:
                    maxid=0
                else:
                    maxid=max(hlids)
                hlids2=[int(item) for item in j.system.fs.listDirsInDir("%s/%s"%(diskpath,maxid), recursive=False, dirNameOnly=True, findDirectorySymlinks=True)]
                if hlids=[]:
                    maxid2=1
                else:
                    maxid2=max(hlids2)                
                self.cidMax[diskid]=maxid*1000+maxid2

    def cid2path(self,diskid,cid):
        hlcid=int(cid/1000)
        llcid=cid-(hlcid*1000)
        return j.system.fs.joinPaths(self.diskid2path[diskid],str(hlcid),"%s.tar"%str(llcid))

    def getActiveWriteContainer(self):
        if self.activeContainer==None or self.activeContainerSize>activeContainerMaxSize or self.activeContainerNrFilesAdded>500:
            diskfreeMax=0
            diskidfound=none
            for diskid,diskpath,diskfree in self.disks:
                if diskfree>diskfreeMax and diskfree>self.diskfreeMinSize:
                    diskfreeMax=diskfree
                    diskidfound=diskid
            if diskidfound==None:
                raise RuntimeError("did not find disk with enough space free")
            if self.activeContainer<>None:
                self.activeContainer.close()
            self.cidMax[diskidfound]+=1
            path=self.cid2path(diskidfound,self.cidMax[diskidfound])
            self.activeContainer=(self.cidMax[diskidfound],tarfile.open(name=path, mode='w:', fileobj=None, bufsize=10240))
        return self.activeContainer

    def cmd2Queue(self,qid=0,cmd="",args={},key="",data="",sync=True):
        rkeyQ="blobserver:cmdqueue:%s"%qid
        jobguid=j.base.idgenerator.generateGUID()     
        if key<>"":
            args["key"]=key
        job=[int(time.time()),jobguid,cmd,args]        
        if data=="":
            self.blobstor.redis.redis.execute_pipeline(\
                ("RPUSH","blobserver:cmdqueue:0",jobguid),\
                ("HSET","blobserver:cmds",jobguid,ujson.dumps(job)))
        elif data<>"":
            self.blobstor.redis.redis.execute_pipeline(\
                ("RPUSH",rkeyQ,jobguid),\
                ("HSET","blobserver:cmds",jobguid,ujson.dumps(job)),\
                ("HSET","blobserver:blob",key,data))
        if sync:
            self.blobstor.redis.redis.execute(cmd="BLPOP", key="blobserver:return:%s"%jobguid)
            self.blobstor.redis.redis.execute(cmd="HDEL", key="blobserver:cmds",subkey=jobguid)
        return jobguid


    #         result=self.queueCMD(cmd="BLPOP", key="blobserver:return:%s"%jobguid, data=timeout,sendnow=True)
    #         self.queueCMD(cmd="HDEL", key="blobserver:cmds",subkey=jobguid) 

    def repCmdServer(self):
        cmdsocket = self.cmdcontext.socket(zmq.REP)
        cmdsocket.connect("inproc://cmdworkers")
        while True:
            parts = cmdsocket.recv_multipart()   
            parts=parts[:-1]         
            deny=False
            for part in parts:
                splitted=part.split("\r\n")
                try:
                    cmd=splitted[2]
                    if len(splitted)>4:
                        key=splitted[4]
                    else:
                        key=""
                except Exception,e:                    
                    raise RuntimeError("could not parse incoming cmds for redis. Error:%s"%e)

                # if cmd not in ("SET","GET","HSET","INCREMENT","RPUSH","LPUSH"):
                #     deny=True
                # if key.find("blobstor")<>0:
                #     deny=True
            if deny==True:
                cmdsocket.send_multipart(["DENY"])
            else:
                self.redis.send_packed_commands(parts)
                result =self.redis.read_n_response(len(parts))            
                if j.basetype.list.check(result[-1]):
                    result=result[-1]
                cmdsocket.send_multipart(result)

    def cmdGreenlet(self):
        # Nonblocking
        self.cmdcontext = zmq.Context()

        frontend = self.cmdcontext.socket(zmq.ROUTER)
        backend = self.cmdcontext.socket(zmq.DEALER)

        frontend.bind("tcp://*:%s" % self.port)
        backend.bind("inproc://cmdworkers")

        # Initialize poll set
        poller = zmq.Poller()
        poller.register(frontend, zmq.POLLIN)
        poller.register(backend, zmq.POLLIN)

        workers = []

        for i in range(self.nrCmdGreenlets):
            workers.append(gevent.spawn(self.repCmdServer))

        while True:
            socks = dict(poller.poll())
            if socks.get(frontend) == zmq.POLLIN:
                parts = frontend.recv_multipart()
                parts.append(parts[0])  # add session id at end
                backend.send_multipart([parts[0]] + parts)

            if socks.get(backend) == zmq.POLLIN:
                parts = backend.recv_multipart()
                frontend.send_multipart(parts[1:])  # @todo dont understand why I need to remove first part of parts?

    def _getPaths(self, namespace, key):
        storpath=j.system.fs.joinPaths(self.STORpath, namespace, key[0:2], key[2:4], key)
        mdpath=storpath + ".md"
        return storpath, mdpath

    def set(self, namespace, key, data, repoId="",serialization="",session=None):
        if serialization=="":
            serialization="lzma"

        if key==None or key=="":
            raise RuntimeError("key cannot be None or empty.")

        cid,tarfile=self.getActiveWriteContainer()

        from IPython import embed
        print "DEBUG NOW set"
        embed()
        s        

        tarinfo=tarfile.TarInfo()
        tarinfo.size=len(data)

        md={}
        md["md5"] = md5
        md["format"] = serialization
        md["repos"] = ""

        if not j.system.fs.exists(path=mdpath):
        else:
            md = ujson.loads(j.system.fs.fileGetContents(mdpath))
        if not md.has_key("repos"):
            md["repos"] = {}
        md["repos"][str(repoId)] = True
        mddata = ujson.dumps(md)
        # print "Set:%s"%md
        j.system.fs.writeFile(storpath + ".md", mddata)
        return [key, True, True]

    def get(self, namespace, key, serialization="", session=None):
        if serialization == "":
            serialization = "lzma"

        storpath, mdpath = self._getPaths(namespace,key)

        if not j.system.fs.exists(storpath):
            # Blob doesn't exist here, let's check with Our Parent Blobstor(s)
            if self._client.exists(namespace, key):
                missing_blob = self._client.get(namespace, key, serialization, session)
                # Set the blob in our BlobStor
                self.set(namespace, key, missing_blob, serialization=serialization, session=session)
                return missing_blob

        md = ujson.loads(j.system.fs.fileGetContents(mdpath))
        if md["format"] != serialization:
            raise RuntimeError("Serialization specified does not exist.") #in future can convert but not now
        with open(storpath) as fp:
            data2 = fp.read()
            fp.close()
        return data2

    def getMD(self,namespace,key,session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        storpath,mdpath=self._getPaths(namespace,key)

        return ujson.loads(j.system.fs.fileGetContents(mdpath))

    def delete(self,namespace,key,repoId="",force=False,session=None):
        if force=='':
            force=False #@todo is workaround default datas dont work as properly, when not filled in always ''
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        if force:
            storpath,mdpath=self._getPaths(namespace,key)
            j.system.fs.remove(storpath)
            j.system.fs.remove(mdpath)
            return

        if key<>"" and not self.exists(namespace,key):
            return

        storpath,mdpath=self._getPaths(namespace,key)

        if not j.system.fs.exists(path=mdpath):
            raise RuntimeError("did not find metadata")
        md=ujson.loads(j.system.fs.fileGetContents(mdpath))
        if not md.has_key("repos"):
            raise RuntimeError("error in metadata on path:%s, needs to have repos as key."%mdpath)
        if md["repos"].has_key(str(repoId)):
            md["repos"].pop(str(repoId))
        if md["repos"]=={}:
            j.system.fs.remove(storpath)
            j.system.fs.remove(mdpath)
        else:
            mddata=ujson.dumps(md)
            j.system.fs.writeFile(storpath+".md",mddata)

    def exists(self,namespace,key, repoId="", session=None):
        storpath,mdpath=self._getPaths(namespace,key)
        if repoId=="":
            return j.system.fs.exists(path=storpath)
        if j.system.fs.exists(path=storpath):
            md=ujson.loads(j.system.fs.fileGetContents(mdpath))
            return md["repos"].has_key(str(repoId))
        return False

    def deleteNamespace(self, namespace, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        storpath=j.system.fs.joinPaths(self.STORpath,namespace)
        j.system.fs.removeDirTree(storpath)

    def getBlobPatch(self, namespace, keyList, session=None):
        """
        Takes a list of Keys, and returns a TAR Archive with All Blobs
        """
        if not keyList:
            raise RuntimeError("Invalid Blobs Key List")

        patch_name = tempfile.mktemp(prefix="blob", suffix=".tar")
        blob_patch = tarfile.open(patch_name, 'w')

        for key in keyList:
            blob_path, _ = self._getPaths(namespace, key)
            if j.system.fs.exists(blob_path):
                # TODO: change blob_path to be easier in extraction instead of full path
                # Now it is added as /opt/STOR/<namespace>/<key0:2>/<key2:4>/<key>
                blob_patch.add(blob_path)

        blob_patch.close()

        # TODO: What if very large Tar?!
        with open(patch_name) as fp:
            data = fp.read()
            fp.close()

        return data



    def start(self, mainloop=None):
        # print "starting %s"%self.name
        self.schedule("cmdGreenlet", self.cmdGreenlet)
        # self.startClock()
        # print "start %s on port:%s"%(self.name,self.port)
        if mainloop <> None:
            mainloop()
        else:
            while True:
                gevent.sleep(100)

