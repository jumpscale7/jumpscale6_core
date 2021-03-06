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
            try:
                self._osis = j.core.osis.getClientByInstance()
            except KeyError:
                return None
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

        if j.__dict__.has_key("processmanager") and j.processmanager.__dict__.has_key("redis_queues"):
            self.redis=j.processmanager.redis_mem
        else:
            self.redis = j.clients.redis.getGeventRedisClient("127.0.0.1", 9999)

        #check we are not running yet, if so kill the other guy
        #make sure no service running with processmanager
        # j.system.process.checkstop("sudo stop processmanager","processmanager.py",nrinstances=1) #@todo
    
    # @property
    # def redisprocessmanager(self):
    #     if not self._redisprocessmanager:
    #         if j.system.net.tcpPortConnectionTest("127.0.0.1",9999)==False:
    #             raise RuntimeError("Could not start processmanager, redis not found on 9999")
    #         self._redisprocessmanager = j.clients.redis.getGeventRedisClient('127.0.0.1', 9999)
    #     return self._redisprocessmanager

    def start(self):
        # #check redis is there if not try to start
        # if not j.system.net.tcpPortConnectionTest("127.0.0.1",9999):
        #     j.packages.findNewest(name="redis").install()
        #     j.packages.findNewest(name="redis").start()

        # wait=1
        # while j.system.net.tcpPortConnectionTest("127.0.0.1",9999)==False:
        #     msg= "cannot connect to redis main, will keep on trying forever, please start redis process manager (port 9999)"    
        #     print msg
        #     j.events.opserror(msg, category='processmanager.startup')    
        #     if wait<60:
        #         wait+=1
        #     time.sleep(wait)

        # wait=1
        # while j.system.net.tcpPortConnectionTest("127.0.0.1",9999)==False:
        #     msg= "cannot connect to redis main, will keep on trying forever, please start redis production (port 9999)"    
        #     print msg
        #     j.events.opserror(msg, category='processmanager.startup')    
        #     if wait<60:
        #         wait+=1
        #     time.sleep(wait)

        # self.redis = j.clients.redis.getGeventRedisClient("127.0.0.1", 9999)
        # self.redis=j.processmanager.redis_mem

        wait=1

        j.core.jumpscripts.loadFromGridMaster()

        osis = self.daemon.osis
        self.daemon = j.servers.geventws.getServer(port=4446)  #@todo no longer needed I think, it should not longer be a socket server, lets check first
        self.daemon.osis = osis
        self.daemon.daemon.osis = osis

        #clean old stuff from redis
        import JumpScale.baselib.redisworker
        j.clients.redisworker.deleteProcessQueue()
        # j.clients.redisworker.deleteJumpscripts() #CANNOT DO NOW BECAUSE ARE STILL RELYING ON ID's so could be someone still wants to execute

        self.redis.set("processmanager:startuptime",str(int(time.time())))

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
        for queuename in ('default', 'io', 'hypervisor', 'process'):
            j.clients.redisworker.redis.lpush("workers:action:%s"%queuename,"RESTART")

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
        if self.daemon.osis:
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
        val=self.redis.get("processmanager:startuptime")
        return int(val)

    def checkStartupOlderThan(self,secago):
        return self.getStartupTime()<int(time.time())-secago

