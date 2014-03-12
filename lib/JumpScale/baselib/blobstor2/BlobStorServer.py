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
            else:
                diskid=self.master.registerDisk(nid=nid,bsnodeid=bsnid, path=item, sizeGB=hrd.getInt("blobstor.disk.size"),\
                    diskId=hrd.getInt("blobstor.disk.id"))


        gevent.monkey.patch_socket()
        GeventLoop.__init__(self)

        self.port = port
        self.nrCmdGreenlets = nrCmdGreenlets

        self.redis=j.clients.blobstor2.redis.redis

        



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

