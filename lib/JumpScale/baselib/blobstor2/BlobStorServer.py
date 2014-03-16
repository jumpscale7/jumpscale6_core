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
import msgpack
import plyvel

GeventLoop = j.core.gevent.getGeventLoopClass()

class BlobStorServer(GeventLoop):

    def __init__(self, port=2345,path="/mnt/BLOBSTOR", nrCmdGreenlets=50):

        j.application.initGrid()

        self.path=path

        self.sessions={}
        self.sessions[""]=None
        
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
        self.bsnid=bsnid
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

        self.activeContainer={}
        self.activeContainerNrFilesAdded={}
        self.activeContainerSize={}        
        self.activeContainerModDate={}
        self.activeContainerFiles={}

        self.activeContainerMaxSize=15*1024*1024
        self.activeContainerExpiration=600
        self.diskfreeMinSizeGB=5

        self.monitorDisks()

        self.db = plyvel.DB('/opt/blobstor/db/', create_if_missing=True)

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
                diskid=self.master.registerDisk(nid=j.application.whoAmI.nid,bsnodeid=self.bsnid, path=item, sizeGB=size, diskId=diskid)
                self.disks.append((diskid,diskpath,diskfree))
                self.diskid2path[diskid]=diskpath
                self.nrdisks+=1

    def getCIDMax(self,namespace):
        if self.cidMax.has_key(namespace):
            return self.cidMax[namespace]

        maxcidOverDisks=0

        for diskid,diskpath,diskfree in self.disks:        
            diskpath2=j.system.fs.joinPaths(diskpath,namespace)
            if not j.system.fs.exists(path=diskpath2):
                j.system.fs.createDir(diskpath2)            
            hlids=[int(item) for item in j.system.fs.listDirsInDir(diskpath2, recursive=False, dirNameOnly=True, findDirectorySymlinks=True)]
            if hlids==[]:
                maxid=0
            else:
                maxid=max(hlids)
            subdir="%s/%s"%(diskpath2,maxid)
            if not j.system.fs.exists(path=subdir):
                j.system.fs.createDir(subdir)

            hlids2=[int(j.system.fs.getBaseName(item)[:-4]) for item in j.system.fs.listFilesInDir(subdir, recursive=False, filter=None)]
            if hlids2==[]:
                maxid2=1
            else:
                maxid2=max(hlids2)

            maxcid=maxid*1000+maxid2

            if maxcid>maxcidOverDisks:
                maxcidOverDisks=maxcid

        self.cidMax[namespace]=maxcidOverDisks

    def cid2path(self,namespace,diskid,cid):
        hlcid=int(cid/1000)
        llcid=cid-(hlcid*1000)
        dpath=j.system.fs.joinPaths(self.diskid2path[diskid],namespace,str(hlcid))
        j.system.fs.createDir(dpath)
        return j.system.fs.joinPaths(dpath,"%s.tar"%str(llcid))

    def getActiveWriteContainer(self,namespace="default",checkonly=False):
        if not self.activeContainer.has_key(namespace) \
                or self.activeContainerSize[namespace]>self.activeContainerMaxSize \
                or self.activeContainerNrFilesAdded[namespace]>200 \
                or self.activeContainerModDate[namespace]<(time.time()-self.activeContainerExpiration):

            print ("SELECT NEW ACTIVE WRITE CONTAINER")

            diskfreeMax=0
            diskidfound=None
            for diskid,diskpath,diskfree in self.disks:
                if diskfree>diskfreeMax and diskfree>self.diskfreeMinSizeGB:
                    diskfreeMax=diskfree
                    diskidfound=diskid
            if diskidfound==None:
                raise RuntimeError("did not find disk with enough space free")

            if self.activeContainer.has_key(namespace):
                self.activeContainer[namespace][2].close()
                self.activeContainer.pop(namespace)

            self.activeContainerNrFilesAdded[namespace]=0
            self.activeContainerSize[namespace]=0
            self.activeContainerModDate[namespace]=0
            self.activeContainerFiles[namespace]=[]       

            self.getCIDMax(namespace)
            self.cidMax[namespace]+=1
            path=self.cid2path(namespace,diskidfound,self.cidMax[namespace])
            self.activeContainer[namespace]=(diskidfound,self.cidMax[namespace],tarfile.open(name=path, mode='w:', fileobj=None, bufsize=10240))
        
        return self.activeContainer[namespace]

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

    def repCmdServer(self):
        cmdsocket = self.cmdcontext.socket(zmq.REP)
        cmdsocket.connect("inproc://cmdworkers")
        while True:
            parts = cmdsocket.recv_multipart()   
            parts=parts[:-1]         
            deny=False
            cmds=msgpack.loads(parts[0])
            sync = "S" in parts[1]
            timeout=int(parts[2])
            key=parts[3]

            for cmd,args,data in cmds:
                if not getattr(self, cmd):
                    cmdsocket.send_multipart([str(1),cmd]) #1 means not found
                    return
                # print cmd               
                if data<>"":
                    method=getattr(self, cmd)
                    res=method(data=data,session=self.sessions[key],**args)
                else:
                    method=getattr(self, cmd)                    
                    res=method(session=self.sessions[key],**args)

                if res=="DENY":
                    cmdsocket.send_multipart([str(2),cmd]) #1 means not found
                    return
            if sync:
                cmdsocket.send_multipart([str(0),msgpack.dumps(res)])
            else:
                cmdsocket.send_multipart([str(0),""])  #will have to be a sort of jobguid which we will then return so followup can be done

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

    def LOGIN(self,login="",passwd="",session=None):
        key=j.base.idgenerator.generateGUID()
        self.sessions[key]=(login,passwd)
        return {"key":key}

    def SET(self, namespace, key, data, repoid=0,serialization="",session=None):
        # if serialization=="":
        #     serialization="lzma"

        if key==None or key=="":
            raise RuntimeError("key cannot be None or empty.")
        key2=b'%s__%s'%(namespace,key)
        mddata=self.db.get(key2)
        if  mddata<>None:
            size,repos,diskid,cid=msgpack.loads(mddata)
            if int(repoid) not in repos:
                repos.append(repoid)
                self.db.put(key2,msgpack.dumps((size,repos,diskid,cid)))
                mdchange=True
            else:
                mdchange=False
            change=False
        else:
            diskid,cid,tf=self.getActiveWriteContainer(namespace)
            tarinfo=tarfile.TarInfo()
            tarinfo.size=len(data)
            tarinfo.name=key
            md={}
            md["format"] = serialization
            # md["repos"] = "%s"%repoid
            tarinfo.pax_headers=md

            tf.addfile(tarinfo, StringIO.StringIO(data))
            self.db.put(key2,msgpack.dumps([tarinfo.size,[int(repoid)],diskid,cid]))

            self.activeContainerModDate[namespace]=time.time()
            self.activeContainerSize[namespace]+=len(data)
            self.activeContainerNrFilesAdded[namespace]+=1
            self.activeContainerFiles[namespace].append(key)

            mdchange=True
            change=True

        return [key, mdchange, change]

    def GET(self, namespace, key, repoid=0,serialization="", session=None):
        # if serialization == "":
        #     serialization = "lzma"
        if key==None or key=="":
            raise RuntimeError("key cannot be None or empty.")
        key2=b'%s__%s'%(namespace,key)
        mddata=self.db.get(key2)
        if  mddata<>None:
            size,repos,diskid,cid=msgpack.loads(mddata)
            if self.activeContainerFiles.has_key(namespace)and key in self.activeContainerFiles[namespace]:
                diskid,cid,tf=self.getActiveWriteContainer(namespace)
                close=False #dont close used for writing
            else:
                path=self.cid2path(namespace,diskid,cid)
                tf=tarfile.open(name=path, mode='r:', fileobj=None, bufsize=10240)
                close=True

            tarinfo=tf.getmember(key)
            f=tf.extractfile(tarinfo)
            data=f.read()
            f.close()
            if close:
                tf.close()
            return data
        else:
            return None

    def GETMD(self,namespace,key,repoid=0,session=None):
        if key==None or key=="":
            raise RuntimeError("key cannot be None or empty.")
        key2=b'%s__%s'%(namespace,key)
        return msgpack.loads(self.db.get(key2))

    def EXISTS(self,namespace,key,repoid=0,session=None):
        if key==None or key=="":
            raise RuntimeError("key cannot be None or empty.")
        key2=b'%s__%s'%(namespace,key)
        return self.db.get(key2)<>None

    def EXISTSBATCH (self, namespace, keys, repoid=0,session=None):
        exists=[]
        for key in keys:
            if self.EXISTS(namespace, key, repoid=repoid, session=session):
                exists.append(key)
        return exists

    def DELETE(self,namespace,key,repoid="",force=False,session=None):
        raise RuntimeError("not implemented")
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
        if md["repos"].has_key(str(repoid)):
            md["repos"].pop(str(repoid))
        if md["repos"]=={}:
            j.system.fs.remove(storpath)
            j.system.fs.remove(mdpath)
        else:
            mddata=ujson.dumps(md)
            j.system.fs.writeFile(storpath+".md",mddata)


    def DELNS(self, namespace, session=None):
        raise RuntimeError("not implemented")
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

