from JumpScale import j
import JumpScale.grid.osis
import JumpScale.baselib.stataggregator
import sys
import psutil
import importlib
import time
import imp

class Dummy():
    pass

class JumpScript(object):
    def __init__(self, ddict):
        self.period = 0
        self.lastrun = 0
        self.startatboot = False
        self.__dict__.update(ddict)
        self.write()
        self.load()

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
        self.module = imp.load_source('JumpScale.jumpscript_%s' % md5sum, self.path)

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
            j.clients.redisworker.execJumpscript(self.id,_timeout=60,_queue=queue,_log=self.log,_sync=False)

        self.lastrun = time.time()
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
        self.daemon=DummyDaemon()
        self.basedir="%s/apps/processmanager"%j.dirs.baseDir
        j.system.platform.psutil=psutil

        #check we are not running yet, if so kill the other guy
        #make sure no service running with processmanager
        j.system.process.checkstop("sudo stop processmanager","processmanager.py",nrinstances=1)
        

    def start(self):
        #check redis is there if not try to start
        if not j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
            j.packages.findNewest(name="redis").install()
            j.packages.findNewest(name="redis").start()

        def checkosis():
            self.daemon.osis

        def checkagentcontroller():
            masterip=j.application.config.get("grid.master.ip")
            client=j.clients.agentcontroller.get(masterip)
            return client
            
        import JumpScale.grid.agentcontroller
        if 'jumpscale__osis' in j.tools.startupmanager.listProcesses():
            j.tools.startupmanager.startProcess("jumpscale","osis")

        masterip=j.application.config.get("grid.master.ip")
        if masterip in j.system.net.getIpAddresses():

            if not j.tools.startupmanager.exists("jumpscale","osis"):
                raise RuntimeError("Could not find osis installed on local system, please install.")

            if not j.tools.startupmanager.exists("jumpscale","agentcontroller"):
                raise RuntimeError("Could not find osis installed on local system, please install.")
            
            if not j.system.net.tcpPortConnectionTest("127.0.0.1",5544):
                j.tools.startupmanager.startProcess("jumpscale","osis")
            if not j.system.net.tcpPortConnectionTest("127.0.0.1",4444):        
                j.tools.startupmanager.startProcess("jumpscale","agentcontroller")

        success=False
        while success==False:
            try:
                checkosis()
                self.acclient=checkagentcontroller()
                success=True
            except Exception,e:
                msg="Cannot connect to osis or agentcontroller on %s, will retry in 60 sec."%(masterip)
                j.events.opserror(msg, category='processmanager.startup', e=e)
                time.sleep(60)

        #check we are mounted over nfs, if not raise error (only when not master)
        if j.system.net.tcpPortConnectionTest("127.0.0.1",int(j.application.config.get("grid.master.port")))==False:
            if self._checkIsNFSMounted()==False:
                raise RuntimeError("code is not mounted to gridmaster")

        self.loadFromAgentController()
        osis = self.daemon.osis
        self.daemon = j.servers.geventws.getServer(port=4445)
        self.daemon.osis = osis
        self.daemon.daemon.osis = osis
        self.loadCmds()

        #ask all running workers to restart
        import JumpScale.baselib.credis
        redis = j.clients.credis.getRedisClient("127.0.0.1", 7768)
        #find workers in mem
        import psutil
        nrworkers=0

        self.starttime=j.base.time.getTimeEpoch()



        def donothing(): #not used yet
            #just to make sure we dont keep waiting for 60 sec
            import time
            time.sleep(0.5)
            print  "DIE"

        j.tools.startupmanager.startAll()

        for proc in psutil.process_iter():
            name2=" ".join(proc.cmdline)
            if name2.find("python worker.py")<>-1:
                workername=name2.split("-wn")[1].strip()
                redis.set("workers:action:%s"%workername,"STOP")

        self.daemon.start()

    def _checkIsNFSMounted(self,check="/opt/code"):
        rc,out=j.system.process.execute("mount")
        found=False
        for line in out.split("\n"):
            if line.find(check)<>-1:
                found=True
        return found


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

        for key in self.daemon.daemon.cmdsInterfaces.keys():
            self.cmds.__dict__[key]=self.daemon.daemon.cmdsInterfaces[key]
            if hasattr(self.cmds.__dict__[key],"_init"):
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

    def loadFromAgentController(self):

        if self._checkIsNFSMounted(check="/opt/code/master"):
            from IPython import embed
            print "DEBUG NOW loadFromAgentController"
            embed()
            
        else:
            #delete previous scripts
            todel=["eventhandling","loghandling","monitoringobjects","processmanagercmds"]
            for delitem in todel:
                j.system.fs.removeDirTree( j.system.fs.joinPaths(self.basedir, delitem))

            #import new code
            #download all monitoring & cmd scripts

            import tarfile
            scripttgz=self.acclient.getProcessmanagerScripts()
            ppath=j.system.fs.joinPaths(j.dirs.tmpDir,"processMgrScripts_%s.tar"%j.base.idgenerator.generateRandomInt(1,1000000))
            j.system.fs.writeFile(ppath,scripttgz)
            tar = tarfile.open(ppath, "r:bz2")

            # tmppath="/tmp/%s"%j.base.idgenerator.generateRandomInt(1,100000)
            for tarinfo in tar:
                if tarinfo.isfile():
                    if tarinfo.name.find("processmanager/")==0:
                        # dest=tarinfo.name.replace("processmanager/","")           
                        tar.extract(tarinfo.name, j.system.fs.getParent(self.basedir))
                        # j.system.fs.createDir(j.system.fs.getDirName(dest))
                        # j.system.fs.moveFile("%s/%s"%(tmppath,tarinfo.name),dest)
            # j.system.fs.removeDirTree(tmppath)
            j.system.fs.remove(ppath)
