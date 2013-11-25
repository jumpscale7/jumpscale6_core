from JumpScale import j
import os
import JumpScale.baselib.screen
import time
import threading
# import Queue

class ProcessDef:
    def __init__(self, hrd):
        self.autostart=hrd.get("process.autostart")
        self.name=hrd.get("process.name")
        self.domain=hrd.get("process.domain")
        self.cmd=hrd.get("process.cmd")
        self.args=hrd.get("process.args")
        self.env=hrd.getDict("process.env")
        self.priority=hrd.getInt("process.priority")
        self.workingdir=hrd.get("process.workingdir")
        self.ports=hrd.getList("process.ports")
        self.jpackage_domain=hrd.get("process.jpackage.domain")
        self.jpackage_name=hrd.get("process.jpackage.name")
        self.jpackage_version=hrd.get("process.jpackage.version")
        self.logfile = j.system.fs.joinPaths(StartupManager.LOGDIR, "%s_%s.log" % (self.domain, self.name))
        self.pid=0
        self.processobject=None
        self._nameLong=self.name
        while len(self._nameLong)<20:
            self._nameLong+=" "

    def _ensure(self):
        sessions = [ s[1] for s in j.system.platform.screen.getSessions() ]
        if self.domain not in sessions:
            self.log("session create START")
            j.system.platform.screen.createSession(self.domain, [self.name])
            self.log("session create OK")
        if self.name not in j.system.platform.screen.listWindows(self.domain):
            self.log("window create START")
            j.system.platform.screen.createWindow(self.domain, self.name)
            self.log("window create OK")

    def log(self,msg):

        print "%s: %s"%(self._nameLong,msg)

    def start(self, timeout=100):
        self._ensure()
        if self.isRunning():
            self.log("no need to start, already started.")
            return
        try:
            jp=j.packages.find(self.jpackage_domain,self.jpackage_name)[0]
        except Exception,e:
            raise RuntimeError("COULD NOT FIND JPACKAGE:%s:%s"%(self.domain,self.name))
            
        self.log("process dependency CHECK")
        jp.processDepCheck(timeout=timeout)
        self.log("process dependency OK")
        self.log("start process")
        j.system.platform.screen.executeInScreen(self.domain,self.name,self.cmd+" "+self.args,cwd=self.workingdir, env=self.env, newscr=True)
        j.system.platform.screen.logWindow(self.domain,self.name,self.logfile)

        self.log("pid get")
        pid=self.getPid(timeout=5)
        self.log("pid: %s"%pid)

        for port in self.ports:
            if not port or not port.isdigit():
                continue
            port = int(port)
            self.log("port check:%s START"%port)
            if not j.system.net.waitConnectionTest('localhost', port, timeout):
                raise RuntimeError('Process %s failed to start listening on port %s withing timeout %s' % (self.name, port, timeout))
            self.log("port check:%s DONE"%port)

        self.log("*** STARTED ***")
        return pid

    def getProcessObject(self):
        pid=self.getPid()
        return self.processobject

    def getPid(self,timeout=5,ifNoPidFail=True):
        if self.pid==0:
            cmd="tmux lsp -a -t j%s -F#{pane_pid},#{window_name}"%self.domain
            exitcode, output = j.system.process.execute(cmd, dieOnNonZeroExitCode=True)
            pid=0
            for line in output.split("\n"):
                line=line.strip()
                if line=="":
                    continue
                pid2,name=line.split(",")
                if name==self.name:
                    pid=int(pid2)

            if pid==0:
                if ifNoPidFail:
                    raise RuntimeError("Could not start %s, pid was not found"%self)
                else:
                    # print "no pid found in cmd:%s"%cmd
                    return 0
                #@todo show errorlog

            pr=j.system.process.getProcessObject(pid)
            

            def check():
                pid=None
                children=pr.get_children()
                if len(children)>0:
                    if len(children)>1:
                        raise RuntimeError("Can max have 1 child")
                    child=children[0]

                    if j.system.process.isPidAlive(child.pid):
                        pid=child.pid
                        self.pid=pid
                        self.processobject=j.system.process.getProcessObject(pid)
                        # print "FOUND:%s"%self.pid
                        return self.pid
                    else:
                        # print "pid not alive for %s"%self
                        return 0
                # print "none"
                return None

            if timeout==0:
                timeout=0.1

            pid=None
            start=j.base.time.getTimeEpoch()            
            now=start
            while now<start+timeout and pid==None:
                pid=check()
                # print "timecheck:%s"%pid
                time.sleep(0.05)
                now=j.base.time.getTimeEpoch()

            if ifNoPidFail==False:
                if pid==None:
                    pid=0
                return pid

            if pid>0:
                return pid
            
            raise RuntimeError("Timeout on wait for chilprocess for tmux for processdef:%s"%self)
            
        return self.pid

    def isRunning(self):
        pid=self.getPid(timeout=0,ifNoPidFail=False)
        if pid==0:
            return False
        test=j.system.process.isPidAlive(pid)
        if test==False:
            return False

        for port in self.ports:
            port = int(port)
            if not j.system.net.checkListenPort(port):
                return False

        return True

    def stop(self, timeout=20):
        pid=self.getPid(timeout=0,ifNoPidFail=False)
        
        if pid==0:
            return 

        pr=self.getProcessObject()
        pr.kill()
        
        if j.system.process.isPidAlive(self.getPid()):
            j.system.platform.screen.killWindow(self.domain, self.name)

    def __str__(self):
        return str("Process: %s_%s"%(self.domain,self.name))

    __repr__ = __str__


class StartupManager:
    DEFAULT_DOMAIN = 'generic'
    LOGDIR = j.system.fs.joinPaths(j.dirs.logDir, 'startupmanager')

    def __init__(self):
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')
        j.system.fs.createDir(self._configpath)
        self.processdefs={}
        self.__init=False
        j.system.fs.createDir(StartupManager.LOGDIR)

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
        if jpackage and jpackage.hrd.exists('jp.process.tcpports'):
            for port in jpackage.hrd.getList('jp.process.tcpports'):
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

    def startJPackage(self,jpackage,timeout=20):
        for pd in self.getProcessDefs4JPackage(jpackage):
            pd.start(timeout)

    def stopJPackage(self,jpackage,timeout=20):        
        for pd in self.getProcessDefs4JPackage(jpackage):
            pd.stop(timeout)

    def existsJPackage(self,jpackage):
        return len(self.getProcessDefs4JPackage(jpackage))>0

    def getProcessDefs4JPackage(self,jpackage):
        result=[]
        for pd in self.getProcessDefs():
            if pd.jpackage_name==jpackage.name and pd.jpackage_domain==jpackage.domain:
                result.append(pd)
        return result

    def _start(self,j,pd):
        # print "thread start:%s"%pd
        try:
            pd.start()
        except Exception,e:
            print "********** ERROR **********"
            print pd
            print e
            from IPython import embed
            print "DEBUG NOW oooo"
            embed()
            
            print "********** ERROR **********"
        # print "thread started:%s"%pd

    def startAll(self):
        # q = Queue.Queue()
        for pd in self.getProcessDefs():          
            if pd.autostart:
                t = threading.Thread(target=self._start, args = (j,pd))
                t.daemon = True
                t.start()                  
                # pd.start()
        while True:
            time.sleep(0.1)

    def restartAll(self):
        for pd in self.getProcessDefs():
            if pd.autostart:
                pd.stop()
                pd.start()

    def removeProcess(self,domain, name):
        self.stopProcess(domain, name)
        servercfg = self._getHRDPath(domain, name)
        if j.system.fs.exists(servercfg):
            j.system.fs.remove(servercfg)
        self.load()

    def getStatus4JPackage(self,jpackage):
        result=True
        for pd in self.getProcessDefs4JPackage(jpackage):
            result=result and self.getStatus(pd.domain,pd.name)
        return result

    def getStatus(self, domain, name):
        """
        get status of process, True if status ok
        """
        result=True
        for processdef in self.getProcessDefs(domain, name):
            result=result & processdef.isRunning()
        return result

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


    def startProcess(self, domain, name, timeout=20):
        for pd in self.getProcessDefs(domain, name):
            pd.start(timeout)

    def stopProcess(self, domain,name, timeout=20):
        for pd in self.getProcessDefs(domain, name):
            pd.stop(timeout)

    def restartProcess(self, domain,name):
        self.stopProcess(domain, name)
        self.startProcess(domain, name)
