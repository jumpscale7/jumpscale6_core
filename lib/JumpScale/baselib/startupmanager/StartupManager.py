from JumpScale import j
import os

# def checkPort(*args, **kwargs):
#     watcher = kwargs['watcher']
#     portstr = watcher.env.get('WAIT_FOR_PORT')
#     if portstr:
#         port = int(portstr)
#         return j.system.net.waitConnectionTest('localhost', port, 20)
#     else:
#         raise RuntimeError('Environment variable WAIT_FOR_PORT is not set')

class ProcessDef:
    def __init__(self, hrd):
        self.name=hrd.get("process.name")
        self.domain=hrd.get("process.domain")
        self.cmd=hrd.get("process.cmd")
        self.args=hrd.get("process.args")
        self.env=hrd.getDict("process.env")
        self.numprocesses=hrd.getInt("process.numprocesses")
        self.priority=hrd.getInt("process.priority")
        self.workingdir=hrd.get("process.workingdir")
        self.ports=hrd.getList("process.ports")
        self.jpackage_domain=hrd.get("process.jpackage.domain")
        self.jpackage_name=hrd.get("process.jpackage.domain")
        self.jpackage_version=hrd.get("process.jpackage.domain")

    def start(self):
        from IPython import embed
        print "DEBUG NOW start"
        embed()
        
    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


        

class StartupManager:
    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')
        self.processdefs={}
        self.__init=False

    def _init(self):
        if self.__init==False:
            self.load()
            self.__init=True

    def addProcess(self, name, cmd, args="", env={}, numprocesses=1, priority=0, shell=False, workingdir=None,jpackage=None,domain="",ports=[]):
        self._init()
        envstr=""
        for key in env.keys():
            envstr+="%s:%s,"%(key,env[key])
        envstr=envstr.rstrip(",")

        hrd="process.name=%s\n"%name
        
        if domain=="" and not jpackage==None:
            domain=jpackage.domain

        hrd+="process.domain=%s\n"%domain
        hrd+="process.cmd=%s\n"%cmd
        hrd+="process.args=%s\n"%args
        hrd+="process.env=%s\n"%envstr
        hrd+="process.numprocesses=%s\n"%numprocesses
        hrd+="process.priority=%s\n"%priority
        hrd+="process.workingdir=%s\n"%workingdir
        pstring=""
        for port in ports:
            pstring+="%s,"%port
        pstring=pstring.rstrip(",")

        hrd+="process.ports=%s\n"%pstring
        if jpackage==None:
            hrd+="process.jpackage.domain=\n"
            hrd+="process.jpackage.name=\n"
            hrd+="process.jpackage.version=\n"
        else:
            hrd+="process.jpackage.domain=%s\n"%jpackage.domain
            hrd+="process.jpackage.name=%s\n"%jpackage.name
            hrd+="process.jpackage.version=%s\n"%jpackage.version

        j.system.fs.writeFile(filename=j.system.fs.joinPaths(self._configpath ,"%s__%s.hrd"%(domain,name)),contents=hrd)

        for item in j.system.fs.listFilesInDir("/etc/init.d"):
            itembase=j.system.fs.getBaseName(item)
            if itembase.lower().find(name)<>-1:
                #found process in init.d
                j.system.process.execute("/etc/init.d/%s stop"%itembase)
                j.system.fs.remove(item)

        for item in j.system.fs.listFilesInDir("/etc/init"):
            itembase=j.system.fs.getBaseName(item)
            if itembase.lower().find(name)<>-1:
                #found process in init
                j.system.process.execute("stop %s"%itembase)
                j.system.fs.remove(item)


    def _getKey(self,domain,name):
        return "%s__%s"%(domain,name)

    def load(self):
        for path in j.system.fs.listFilesInDir(self._configpath , recursive=False,filter="*.hrd"):
            domain,name=j.system.fs.getBaseName(path).replace(".hrd","").split("__")
            key="%s__%s"%(domain,name)
            self.processdefs[key]=ProcessDef(j.core.hrd.getHRD(path))


    def startJPackage(self,jpackage):
        from IPython import embed
        print "DEBUG NOW startjpackage"
        embed()
        

    def removeProcess(self,name):
        servercfg = self._getIniFilePath(name)
        if j.system.fs.exists(servercfg):
            j.system.fs.remove(servercfg)
        from IPython import embed
        print "DEBUG NOW removeprocess"
        embed()
        

    def status(self, process=None):
        """
        get status of process if not process is given return status of circus
        """
        status = j.tools.circus.client.status()
        if process:
            return status['statuses'].get(process, 'notfound')
        else:
            return status['status']

    def apply(self):
        """
        make sure circus knows about it
        """
        from IPython import embed
        print "DEBUG NOW apply"
        embed()
        

    def listProcesses(self):
        from IPython import embed
        print "DEBUG NOW listProcesses"
        embed()

    def startProcess(self, domain,name):
        j.tools.circus.client.startWatcher(name)

    def stopProcess(self, domain,name):
        j.tools.circus.client.stopWatcher(name)

    def restartProcess(self, domain,name):
        j.tools.circus.client.restartWatcher(name)

    def reloadProcess(self, domain,name):
        j.tools.circus.client.reloadWatcher(name)
