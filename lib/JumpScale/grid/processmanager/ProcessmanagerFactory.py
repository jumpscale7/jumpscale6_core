from JumpScale import j
import JumpScale.grid.osis
import JumpScale.baselib.stataggregator
import JumpScale.grid.jumpscripts
import sys
import psutil
import importlib
import time
import imp
import inspect
import linecache
import JumpScale.baselib.redis

class Dummy():
    pass

class JumpScript(object):
    def __init__(self, ddict=None, path=None):
        self.period = 0
        self.lastrun = 0
        self.id = None
        self.startatboot = False
        if ddict:
            self.__dict__.update(ddict)
        if not path:
            self.write()
            self.load()
        else:
            self.path = path
            self.load()
            self.loadAttributes()

    def write(self):
        jscriptdir = j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts", self.organization)
        j.system.fs.createDir(jscriptdir)
        self.path=j.system.fs.joinPaths(jscriptdir, "%s.py" % self.name)

        content="""
from JumpScale import j

"""
        content += self.source
        j.system.fs.writeFile(filename=self.path, contents=content)

    def load(self):
        md5sum = j.tools.hash.md5_string(self.path)
        modulename = 'JumpScale.jumpscript_%s' % md5sum
        linecache.checkcache(self.path)
        self.module = imp.load_source(modulename, self.path)

    def getDict(self):
        result = dict()
        for attrib in ('name', 'author', 'organization', 'category', 'license', 'version', 'roles', 'source', 'path', 'descr', 'queue', 'async', 'period', 'order', 'log', 'enable', 'startatboot', 'gid', 'id'):
            result[attrib] = getattr(self, attrib)
        return result

    def loadAttributes(self):
        name = getattr(self.module, 'name', "")
        if name=="":
            name=j.system.fs.getBaseName(self.path)
            name=name.replace(".py","").lower()

        source = inspect.getsource(self.module)
        self.name=name
        self.author=getattr(self.module, 'author', "unknown")
        self.organization=getattr(self.module, 'organization', "unknown")
        self.category=getattr(self.module, 'category', "unknown")
        self.license=getattr(self.module, 'license', "unknown")
        self.version=getattr(self.module, 'version', "1.0")
        self.roles=getattr(self.module, 'roles', [])
        self.source=source
        self.descr=self.module.descr
        self.queue=getattr(self.module, 'queue',"default")
        self.async = getattr(self.module, 'async',False)
        self.period=getattr(self.module, 'period',0)
        self.order=getattr(self.module, 'order', 1)
        self.log=getattr(self.module, 'log', True)
        self.enable=getattr(self.module, 'enable', True)
        self.startatboot=getattr(self.module, 'startatboot', False)
        self.gid=getattr(self.module, 'gid', j.application.whoAmI.gid)

    def run(self, *args, **kwargs):
        return self.module.action(*args, **kwargs)

    def execute(self, *args, **kwargs):
        result = None, None
        if not self.enable:
            return
        if not self.async:
            try:
                result = True, self.run(*args, **kwargs)
            except Exception,e:
                eco=j.errorconditionhandler.parsePythonErrorObject(e)
                eco.errormessage='Exec error procmgr jumpscr:%s_%s on node:%s_%s %s'%(self.organization,self.name, \
                        j.application.whoAmI.gid, j.application.whoAmI.nid,eco.errormessage)
                eco.tags="jscategory:%s"%self.category
                eco.tags+=" jsorganization:%s"%self.organization
                eco.tags+=" jsname:%s"%self.name
                j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
                eco.tb = None
                eco.type = str(eco.type)
                result = False, eco.__dict__
        else:
            # self.q_d.enqueue('%s_%s.action'%(action.organization,action.name))
            #NO LONGER USE redisq, now use our own queuing mechanism
            queue = getattr(self, 'queue', 'default')            
            result=j.clients.redisworker.execJumpscript(self.id,_timeout=60,_queue=queue,_log=self.log,_sync=False)

        self.lastrun = time.time()
        if result<>None:
            print "ok:%s"%self.name
        return result

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
            masterip=j.application.config.get("grid.master.ip")
            success=False
            wait=1
            while success == False:
                try:
                    client=j.clients.agentcontroller.get(masterip)
                    success=True
                except Exception,e:
                    msg="Cannot connect to agentcontroller on %s."%(masterip)
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

