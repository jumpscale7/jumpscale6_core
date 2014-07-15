from JumpScale import j
import JumpScale.grid.osis
import JumpScale.baselib.stataggregator
import JumpScale.grid.jumpscripts
import sys
import psutil
import importlib
import time
import JumpScale.baselib.redis

class Dummy():
    pass

class DummyDaemon():
    def __init__(self):
        self.cmdsInterfaces={}
        self._osis = None

    def _adminAuth(self,user,passwd):
        raise RuntimeError("permission denied")

    @property
    def osis(self):
        if not self._osis:
            masterip=j.application.config.get("grid.master.ip")
            self._osis = j.core.osis.getClient(masterip, user='root')
        return self._osis

    def addCMDsInterface(self, cmdInterfaceClass, category):
        if not self.cmdsInterfaces.has_key(category):
            self.cmdsInterfaces[category] = []
        self.cmdsInterfaces[category].append(cmdInterfaceClass())

class ProcessmanagerFactory:

    """
    """
    def __init__(self):
        self.daemon = DummyDaemon()
        self.basedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'processmanager')
        j.system.platform.psutil = psutil
        self._redisprocessmanager = None

        #check we are not running yet, if so kill the other guy
        #make sure no service running with processmanager
        # j.system.process.checkstop("sudo stop processmanager","processmanager.py",nrinstances=1) #@todo
    
    @property
    def redisprocessmanager(self):
        if not self._redisprocessmanager:
            if j.system.net.tcpPortConnectionTest("127.0.0.1",7766)==False:
                raise RuntimeError("Could not start processmanager, redis not found on 7766")
            self._redisprocessmanager = j.clients.redis.getGeventRedisClient('127.0.0.1', 7766)
        return self._redisprocessmanager

    def start(self):
        # #check redis is there if not try to start
        # if not j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
        #     j.packages.findNewest(name="redis").install()
        #     j.packages.findNewest(name="redis").start()

        wait=1
        while j.system.net.tcpPortConnectionTest("127.0.0.1",7766)==False:
            msg= "cannot connect to redis main, will keep on trying forever, please start redis process manager (port 7766)"    
            print msg
            j.events.opserror(msg, category='processmanager.startup')    
            if wait<60:
                wait+=1
            time.sleep(wait)

        wait=1
        while j.system.net.tcpPortConnectionTest("127.0.0.1",7768)==False:
            msg= "cannot connect to redis main, will keep on trying forever, please start redis production (port 7768)"    
            print msg
            j.events.opserror(msg, category='processmanager.startup')    
            if wait<60:
                wait+=1
            time.sleep(wait)

        self.redis = j.clients.redis.getGeventRedisClient("127.0.0.1", 7768)

        wait=1
        gridmasterip = j.application.config.get('grid.master.ip')
        while j.system.net.tcpPortConnectionTest(gridmasterip, 5544)==False:
            msg="cannot connect to agentcontroller osis, will keep on trying forever, please make sure is started"
            print msg
            j.events.opserror(msg, category='processmanager.startup')    
            if wait<60:
                wait+=1
            time.sleep(wait)

        wait=1
        while j.system.net.tcpPortConnectionTest(gridmasterip, 4444)==False:
            msg= "cannot connect to agentcontroller, will keep on trying forever, please make sure is started"
            print msg
            j.events.opserror(msg, category='processmanager.startup')    
            if wait<60:
                wait+=1
            time.sleep(wait)        

            
        import JumpScale.grid.agentcontroller

        if gridmasterip in j.system.net.getIpAddresses():

            if not j.tools.startupmanager.exists("jumpscale","osis"):
                raise RuntimeError("Could not find osis installed on local system, please install.")

            if not j.tools.startupmanager.exists("jumpscale","agentcontroller"):
                raise RuntimeError("Could not find osis installed on local system, please install.")
            
            if not j.system.net.tcpPortConnectionTest("127.0.0.1",5544):
                j.tools.startupmanager.startProcess("jumpscale","osis")
            if not j.system.net.tcpPortConnectionTest("127.0.0.1",4444):        
                j.tools.startupmanager.startProcess("jumpscale","agentcontroller")


        def checkagentcontroller():
            success=False
            wait=1
            while success == False:
                try:
                    client=j.clients.agentcontroller.get()
                    success=True
                except Exception,e:
                    msg="Cannot connect to agentcontroller."
                    j.events.opserror(msg, category='worker.startup', e=e)
                    if wait<60:
                        wait+=1                    
                    time.sleep(wait)
            return client

        self.acclient=checkagentcontroller()

        j.tools.jumpscriptsManager.loadFromGridMaster()        

        osis = self.daemon.osis
        self.daemon = j.servers.geventws.getServer(port=4445)  #@todo no longer needed I think, it should not longer be a socket server, lets check first
        self.daemon.osis = osis
        self.daemon.daemon.osis = osis

        #clean old stuff from redis
        import JumpScale.baselib.redisworker
        j.clients.redisworker.deleteProcessQueue()
        # j.clients.redisworker.deleteJumpscripts() #CANNOT DO NOW BECAUSE ARE STILL RELYING ON ID's so could be someone still wants to execute

        self.redisprocessmanager.set("processmanager:startuptime",str(int(time.time())))

        self.starttime=j.base.time.getTimeEpoch()

        self.loadCmds()

        # j.tools.startupmanager.startAll()#better not to do this, gives weird results

        self.cmds.jumpscripts.schedule()
                
        self.daemon.start()

    def _checkIsNFSMounted(self,check="/opt/code"):
        rc,out=j.system.process.execute("mount")
        found=False
        for line in out.split("\n"):
            if line.find(check)<>-1:
                found=True
        return found

    def restartWorkers(self):

        for worker in [item for item in j.tools.startupmanager.listProcesses() if item.find("workers")==0]:
            domain,name=worker.split("__")
            pdef=j.tools.startupmanager.getProcessDef(domain,name)
            for nr in range(1,pdef.numprocesses+1):
                workername="%s_%s"%(pdef.name,nr)
                self.redisprocessmanager.set("workers:action:%s"%workername,"STOP")
                if not self.redisprocessmanager.hexists("workers:watchdog",workername):
                    self.redisprocessmanager.hset("workers:watchdog",workername,0)

    def getCmdsObject(self,category):
        if self.cmds.has_key(category):
            return self.cmds["category"]
        else:
            raise RuntimeError("Could not find cmds with category:%s"%category)

    def loadCmds(self):
        if self.basedir not in sys.path:
            sys.path.insert(0, self.basedir)
        cmds=j.system.fs.listFilesInDir(j.system.fs.joinPaths(self.basedir,"processmanagercmds"),filter="*.py")
        cmds.sort()
        for item in cmds:
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                module = importlib.import_module('processmanagercmds.%s' % name)
                classs = getattr(module, name)
                print "load cmds object:%s"%name
                tmp=classs(daemon=self.daemon)
                self.daemon.addCMDsInterface(classs, category=tmp._name)

        self.cmds=Dummy()
        self.loadMonitorObjectTypes()

        def sort(item):
            key,cmd=item
            return getattr(cmd, 'ORDER', 10000)        

        for key, cmd in sorted(self.daemon.daemon.cmdsInterfaces.iteritems(), key=sort):

            self.cmds.__dict__[key]=cmd
            if hasattr(self.cmds.__dict__[key],"_init"):
                print "### INIT ###:%s"%key
                self.cmds.__dict__[key]._init()

    def loadMonitorObjectTypes(self):
        if self.basedir not in sys.path:
            sys.path.insert(0, self.basedir)
        self.monObjects=Dummy()
        for item in j.system.fs.listFilesInDir(j.system.fs.joinPaths(self.basedir,"monitoringobjects"),filter="*.py"):
            name=j.system.fs.getBaseName(item).replace(".py","")
            if name[0]<>"_":
                monmodule = importlib.import_module('monitoringobjects.%s' % name)
                classs=getattr(monmodule, name)
                print "load monitoring object:%s"%name
                factory = getattr(monmodule, '%sFactory' % name)(self, classs)
                self.monObjects.__dict__[name.lower()]=factory   

    def getStartupTime(self):
        val=self.redisprocessmanager.get("processmanager:startuptime")
        return int(val)

    def checkStartupOlderThan(self,secago):
        return self.getStartupTime()<int(time.time())-secago

