from JumpScale import j
import os
import JumpScale.baselib.screen

class ProcessDef:
    def __init__(self, hrd):
        self.start=hrd.get("process.start")
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

    def _ensureDomain(self):
        sessions = [ s[1] for s in j.system.platform.screen.getSessions() ]
        if self.domain not in sessions:
            j.system.platform.screen.createSession(self.domain, [self.name])

    def startdo(self, timeout=60):
        self._ensureDomain()
        jp=j.packages.find(self.domain,self.name)[0]
        jp.processDepCheck(timeout=timeout)
        if self.workingdir:
            j.system.platform.screen.executeInScreen(self.domain,self.name,"cd %s"%self.workingdir,wait=0)
        for key, value in self.env.iteritems():
            cmd = "export %s=%s" % (key, value)
            j.system.platform.screen.executeInScreen(self.domain,self.name,cmd, wait=0)
        j.system.platform.screen.executeInScreen(self.domain,self.name,self.cmd+" "+self.args,wait=0)

    def __str__(self):
        return str(self.__dict__)

    __repr__ = __str__


class StartupManager:
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
        for item in ["byobu","screen"]:
            cmd="killall %s"%item
            j.system.process.execute(cmd,dieOnNonZeroExitCode=False)
        self.init()

    def _init(self):
        if self.__init==False:
            self.load()
            self.__init=True

    def addProcess(self, name, cmd, args="", env={}, numprocesses=1, priority=0, shell=False, workingdir='',jpackage=None,domain="",ports=[],start=True):
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
        if start:
            start=1
        hrd+="process.start=%s\n"%start
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
        self.processdefs={}
        for path in j.system.fs.listFilesInDir(self._configpath , recursive=False,filter="*.hrd"):
            domain,name=j.system.fs.getBaseName(path).replace(".hrd","").split("__")
            key="%s__%s"%(domain,name)
            self.processdefs[key]=ProcessDef(j.core.hrd.getHRD(path))

    def getProcessDefs(self,domain=None,name=None):
        self._init()
        resultOrder={}
        for pd in self.processdefs.itervalues():
            # print "find:%s"%pd
            found=True
            if domain<>None:
                found=found and pd.domain==domain
            if name<>None:
                found=found and pd.name==name
            if found:
                if not resultOrder.has_key(pd.priority):
                    resultOrder[pd.priority]=[]
                resultOrder[pd.priority].append(pd)

        prioritys=resultOrder.keys()
        prioritys.sort()
        result=[]
        for priority in prioritys:
            # print priority
            result+=resultOrder[priority]

        return result

    def getDomains(self):
        result=[]
        for pd in self.processdefs.itervalues():
            if pd.domain not in result:
                result.append(pd.domain)
        return result

    def startJPackage(self,jpackage,timeout=60):
        for pd in self.getProcessDefs(jpackage.domain,jpackage.name):
            pd.startdo()

    def startAll(self):
        for pd in self.getProcessDefs():
            if pd.start:
                "start:%s"%pd
                pd.startdo()

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
        pass #nothing needed any more, was for circus

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


    def startProcess(self, domain, name):
        jp = self._getJPackage(domain, name)
        self.startJPackage(jp)

    def stopProcess(self, domain,name):
        j.tools.circus.client.stopWatcher(name)

    def restartProcess(self, domain,name):
        j.tools.circus.client.restartWatcher(name)

    def reloadProcess(self, domain,name):
        j.tools.circus.client.reloadWatcher(name)
