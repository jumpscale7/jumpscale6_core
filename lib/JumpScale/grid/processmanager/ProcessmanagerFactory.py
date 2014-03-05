from JumpScale import j
import sys
import psutil
import importlib
import time

class Dummy():
    pass

class DummyDaemon():
    def __init__(self):
        self.cmdsInterfaces={}
    def _adminAuth(self,user,passwd):
        raise RuntimeError("permission denied")

    def addCMDsInterface(self, cmdInterfaceClass, category):
        if not self.cmdsInterfaces.has_key(category):
            self.cmdsInterfaces[category] = []
        self.cmdsInterfaces[category].append(cmdInterfaceClass())

class ProcessmanagerFactory:

    """
    """
    def __init__(self):
        self.daemon=DummyDaemon()
        self.basedir="/opt/jumpscale/apps/processmanager"
        j.system.platform.psutil=psutil

    def start(self):
        #check redis is there if not try to start
        if not j.system.net.tcpPortConnectionTest("127.0.0.1",7768):
            j.packages.findNewest(name="redis").install()
            j.packages.findNewest(name="redis").start()

        def checkosis():
            masterip=j.application.config.get("grid.master.ip")
            osis = j.core.osis.getClient(masterip, user='root')

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

        self.loadFromAgentController()
        self.daemon = j.servers.geventws.getServer(port=4445)
        self.loadCmds()
        self.daemon.start()

    def getCmdsObject(self,category):
        if self.cmds.has_key(category):
            return self.cmds["category"]
        else:
            raise RuntimeError("Could not find cmds with category:%s"%category)

    def loadCmds(self):
        sys.path.append(self.basedir)        
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
