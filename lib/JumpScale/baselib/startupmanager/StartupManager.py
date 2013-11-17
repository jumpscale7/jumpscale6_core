from JumpScale import j
import os
import JumpScale.baselib.screen

DEFAULT_TIMEOUT = 60

class ProcessDef:
    def __init__(self, hrd):
        self.autostart=hrd.get("process.autostart")
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

    def _ensure(self):
        sessions = [ s[1] for s in j.system.platform.screen.getSessions() ]
        if self.domain not in sessions:
            j.system.platform.screen.createSession(self.domain, [self.name])
        if self.name not in j.system.platform.screen.listWindows(self.domain):
            j.system.platform.screen.createWindow(self.domain, self.name)

    def start(self, timeout=DEFAULT_TIMEOUT):
        self._ensure()
        jp=j.packages.find(self.domain,self.name)[0]
        jp.processDepCheck(timeout=timeout)
        j.system.platform.screen.executeInScreen(self.domain,self.name,self.cmd+" "+self.args,cwd=self.workingdir, env=self.env, newscr=True)
        for port in self.ports:
            port = int(port)
            if not j.system.net.waitConnectionTest('localhost', port, timeout):
                raise RuntimeError('Process %s failed to start listening on port %s withing timeout %s' % (self.name, port, timeout))

    def stop(self, timeout=DEFAULT_TIMEOUT):
        j.system.platform.screen.killWindow(self.domain, self.name)

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


class StartupManager:
    DEFAULT_DOMAIN = 'generic'

    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')
        self.processdefs={}
        self.__init=False

    def init(self):
        """
        start base for byobu
        """
        for domain in self.getDomains():
            screens=[item.name for item in self.getProcessDefs(domain=domain)]
            j.system.platform.screen.createSession(domain,screens)

    def reset(self):
        self.load()
        #kill remainders
        for item in ["byobu","tmux"]:
            cmd="killall %s"%item
            j.system.process.execute(cmd,dieOnNonZeroExitCode=False)
        self.init()

    def _init(self):
        if self.__init==False:
            self.load()
            self.__init=True

    def addProcess(self, name, cmd, args="", env={}, numprocesses=1, priority=0, shell=False, workingdir='',jpackage=None,domain="",ports=[],autostart=True):
        envstr=""
        for key in env.keys():
            envstr+="%s:%s,"%(key,env[key])
        envstr=envstr.rstrip(",")

        hrd="process.name=%s\n"%name
        if not domain:
            if jpackage:
                domain = jpackage.domain
            else:
                domain = StartupManager.DEFAULT_DOMAIN

        hrd+="process.domain=%s\n"%domain
        hrd+="process.cmd=%s\n"%cmd
        hrd+="process.args=%s\n"%args
        hrd+="process.env=%s\n"%envstr
        hrd+="process.numprocesses=%s\n"%numprocesses
        hrd+="process.priority=%s\n"%priority
        hrd+="process.workingdir=%s\n"%workingdir
        if autostart:
            autostart=1
        hrd+="process.autostart=%s\n"%autostart
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

        j.system.fs.writeFile(filename=self._getHRDPath(domain, name),contents=hrd)

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
        self.load()

    def _getKey(self,domain,name):
        return "%s__%s"%(domain,name)

    def _getHRDPath(self, domain, name):
        return j.system.fs.joinPaths(self._configpath ,"%s.hrd"%(self._getKey(domain,name)))

    def load(self):
        self.processdefs={}
        for path in j.system.fs.listFilesInDir(self._configpath , recursive=False,filter="*.hrd"):
            domain,name=j.system.fs.getBaseName(path).replace(".hrd","").split("__")
            key=self._getKey(domain,name)
            self.processdefs[key]=ProcessDef(j.core.hrd.getHRD(path))

    def getProcessDefs(self,domain=None,name=None):
        self._init()
        def processFilter(process):
            if domain and process.domain != domain:
                return False
            if name and process.name != name:
                return False
            return True

        processes = filter(processFilter, self.processdefs.values())
        processes.sort(key=lambda pd: pd.priority)
        return processes

    def getDomains(self):
        result=[]
        for pd in self.processdefs.itervalues():
            if pd.domain not in result:
                result.append(pd.domain)
        return result

    def startJPackage(self,jpackage,timeout=DEFAULT_TIMEOUT):
        self.startProcess(jpackage.domain, jpackage.name, timeout)

    def stopJPackage(self,jpackage,timeout=DEFAULT_TIMEOUT):
        self.stopProcess(jpackage.domain, jpackage.name, timeout)

    def startAll(self):
        for pd in self.getProcessDefs():
            if pd.autostart:
                pd.start()

    def removeProcess(self,domain, name):
        self.stopProcess(domain, name)
        servercfg = self._getHRDPath(domain, name)
        if j.system.fs.exists(servercfg):
            j.system.fs.remove(servercfg)
        self.load()

    def getStatus(self, domain, name):
        """
        get status of process if not process is given return status
        """
        return j.system.platform.screen.windowExists(domain, name)

    def listProcesses(self):
        files = j.system.fs.listFilesInDir(self._configpath, filter='*.hrd')
        result = list()
        for file_ in files:
            file_ = j.system.fs.getBaseName(file_)
            file_ = os.path.splitext(file_)[0]
            result.append(file_)
        return result

    def _getJPackage(self, domain, name):
        jps = j.packages.find(domain, name, installed=True)
        if not jps:
            raise RuntimeError('Could not find installed jpackage with domain %s and name %s' % (domain, name))
        return jps[0]


    def startProcess(self, domain, name, timeout=DEFAULT_TIMEOUT):
        for pd in self.getProcessDefs(domain, name):
            pd.start(timeout)

    def stopProcess(self, domain,name, timeout=DEFAULT_TIMEOUT):
        for pd in self.getProcessDefs(domain, name):
            pd.stop(timeout)

    def restartProcess(self, domain,name):
        self.stopProcess(domain, name)
        self.startProcess(domain, name)
