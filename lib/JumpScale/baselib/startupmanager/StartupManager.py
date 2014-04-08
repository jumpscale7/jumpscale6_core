from JumpScale import j
import os
import JumpScale.baselib.screen
import time
import threading


class ProcessNotFoundException(Exception):
    pass

class ProcessDef:
    def __init__(self, hrd,path):
        self.hrd=hrd
        self.autostart=hrd.getInt("process.autostart")==1
        self.path=path
        self.name=hrd.get("process.name")
        self.domain=hrd.get("process.domain")
        
        self.user=hrd.get("process.user",checkExists=True)
        if self.user==False:
            self.user="root"
        self.cmd=hrd.get("process.cmd")
        self.args=hrd.get("process.args")
        self.env=hrd.getDict("process.env")
        self.priority=hrd.getInt("process.priority")
        if hrd.exists("process.check"):
            self.checkpid=hrd.getInt("process.check")==1
        else:
            self.checkpid=True

        if hrd.exists("process.timeoutcheck"):
            self.timeout=hrd.getInt("process.timeoutcheck")
        else:
            self.timeout=10
        if self.timeout<2:
            self.timeout=2

        self.reload_signal=0
        if hrd.exists('process.reloadsignal'):
            self.reload_signal = hrd.getInt("process.reloadsignal")
        self.stopcmd = None
        if hrd.exists('process.stopcmd'):
            self.stopcmd = hrd.get("process.stopcmd")
        self.workingdir=hrd.get("process.workingdir")
        self.ports=hrd.getList("process.ports")
        self.ports=[port for port in self.ports if str(port).strip()<>""]
        self.jpackage_domain=hrd.get("process.jpackage.domain")
        self.jpackage_name=hrd.get("process.jpackage.name")
        self.jpackage_version=hrd.get("process.jpackage.version")

        self.logfile = j.system.fs.joinPaths(StartupManager.LOGDIR, "%s_%s_%s.log" % (self.domain, self.name,j.base.time.get5MinuteId()))
        if not j.system.fs.exists(self.logfile):
            j.system.fs.createDir(StartupManager.LOGDIR)
            j.system.fs.createEmptyFile(self.logfile)
        self._nameLong=self.name
        while len(self._nameLong)<20:
            self._nameLong+=" "
        self.lastCheck=0
        self.lastMeasurements={}
        self.active=None
        self.pid=0

    def getJSPid(self):
        return "g%s.n%s.%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid,self.name)

    def log(self,msg):
        print "%s: %s"%(self._nameLong,msg)

    def start(self):
        # self.logToStartupLog("***START***")

        if self.autostart==False:
            self.log("no need to start, disabled.")
            return

        if self.isRunning(wait=False):
            self.log("no need to start, already started.")
            return

        try:
            jp=j.packages.find(self.jpackage_domain,self.jpackage_name)[0]
        except Exception,e:
            raise RuntimeError("COULD NOT FIND JPACKAGE:%s:%s"%(self.domain,self.name))

        self.log("process dependency CHECK")
        jp.processDepCheck()
        self.log("process dependency OK")
        self.log("start process")
        j.system.platform.screen.executeInScreen(self.domain,self.name,self.cmd+" "+self.args,cwd=self.workingdir, env=self.env,user=self.user)#, newscr=True)        
        j.system.platform.screen.logWindow(self.domain,self.name,self.logfile)
                
        isrunning=self.isRunning(wait=True)

        if isrunning and self.checkpid and self.pid==0:
            #means we did not check pid yet as part of isRunning test
            self.getPid(ifNoPidFail=False,wait=False) #we already waited for running test

        self.log("pid: %s"%self.pid)

        if isrunning==False:
            raise RuntimeError("Could not start process:%s, an error occured:\n%s"%(self,self.getStartupLog()))
            
        self.log("*** STARTED ***")
        return self.pid

    def getStartupLog(self):
        if j.system.fs.exists(self.logfile):
            content=j.system.fs.fileGetContents(self.logfile)
            return content
        else:
            content=""
        return content        

    def showLogs(self, command='less -R'):
        if j.system.fs.exists(self.logfile):
            j.system.process.executeWithoutPipe("%s %s" % (command, self.logfile))
        else:
            print "No logs found for %s" % self

    def getProcessObject(self):
        pid=self.getPid(ifNoPidFail=False,wait=False)
        if pid==0:
            return None
        self.processobject=j.system.process.getProcessObject(pid)
        return self.processobject

    def getPid(self,ifNoPidFail=True,wait=False):
        #first check screen is already there with window, max waiting 1 sec        
        now=0
        pid0=None

        if wait:
            start=time.time()
            timeout=start+self.timeout
        else:
            timeout=1 #should not be 0 otherwise dont go in while loop

        while pid0==None and now<timeout:
            pid0 = j.system.platform.screen.getPid(self.domain, self.name)
            if pid0<>0 or wait==False:
                break
            time.sleep(0.2)
            now=time.time()

        if pid0==None:
            if ifNoPidFail:
                raise RuntimeError("Pid was not found for %s, because window not found."%self)
            else:
                return 0

        pr=j.system.process.getProcessObject(pid0)

        def check():
            pid=None
            children=pr.get_children()
            if len(children)>0:
                if len(children)>1:
                    raise RuntimeError("Can max have 1 child")
                child=children[0]

                if child.is_running():
                    pid=child.pid
                    return pid
                else:
                    return 0
            return 0

        pid=0
        now=0
        while pid==0 and now<timeout:
            pid=check()
            if pid<>0 or wait==False:
                break            
            # print "timecheck:%s"%pid
            time.sleep(0.1)
            now=time.time()

        self.pid=pid

        if ifNoPidFail==False:
            return self.pid
        if self.pid>0:
            return self.pid
        raise RuntimeError("Timeout on wait for childprocess for tmux for processdef:%s"%self)

    def _portCheck(self):
        for port in self.ports:
            if port:
                if isinstance(port, basestring) and not port.strip():
                    continue
                port = int(port)
                if not j.system.net.checkListenPort(port):
                    self.hrd.set('process_active', False)
                    return False
        self.hrd.set('process_active', True)
        return True        

    def portCheck(self,wait=False):
        if wait==False:
            return self._portCheck()
        timeout=time.time()+self.timeout
        isrunning=False            
        while time.time()<timeout:
            if self._portCheck():
                return True
            time.sleep(0.05)
        return False

    def isRunning(self,wait=False):

        if self.autostart==False:
            return False

        if self.ports<>[]:
            res= self.portCheck(wait=wait)
            return res

        pid=self.getPid(ifNoPidFail=False,wait=wait)
        if pid==0:
            return False
        test=j.system.process.isPidAlive(pid)
        if test==False:
            return False
        return True

    def stop(self):    
                     
        pid=self.getPid(ifNoPidFail=False,wait=False)
        if pid<>0 and self.getProcessObject() and self.processobject.is_running():
            if not self.stopcmd:
                self.processobject.kill()
            else:
                j.system.process.execute(self.stopcmd)
            start=time.time()
            now=0
            while now<start+self.timeout:
                if self.processobject.is_running()==False:
                    self.log("isdown:%s"%self)
                    break
                time.sleep(0.05)
                now=j.base.time.getTimeEpoch()

        for port in self.ports:        
            if port=="" or port==None or not port.isdigit():                
                raise RuntimeError("port cannot be none for %s"%self)    
            j.system.process.killProcessByPort(port)

        if self.ports<>[]:
            timeout=time.time()+self.timeout
            isrunning=True            
            while time.time()<timeout:
                if self._portCheck()==False:
                    isrunning=False
                    break
                time.sleep(0.05)
            if isrunning:
                raise RuntimeError("Cannot stop, tried portkill, %s"%self)

        j.system.platform.screen.killWindow(self.domain, self.name)

        start=time.time()
        now=0
        windowdown=False
        while windowdown==False and now<start+2:
            if j.system.platform.screen.windowExists(self.domain, self.name)==False:
                windowdown=True
                break
            time.sleep(0.1)
            now=j.base.time.getTimeEpoch()

        if windowdown==False:
            raise RuntimeError("Window was not down yet within 2 sec for %s"%self)

    def disable(self):
        self.stop()
        hrd=j.core.hrd.getHRD(self.path)
        hrd.set("process.autostart",0)
        self.autostart=False

    def enable(self):
        hrd=j.core.hrd.getHRD(self.path)
        hrd.set("process.autostart",1)
        self.autostart=True

    def restart(self):
        self.stop()
        self.start()

    def reload(self):
        if self.reload_signal and self.getProcessObject():
            self.processobject.send_signal(self.reload_signal)
        else:
            self.restart()

    def __str__(self):
        return str("Process: %s_%s\n"%(self.domain,self.name))

    __repr__ = __str__


class StartupManager:
    DEFAULT_DOMAIN = 'generic'
    LOGDIR = j.system.fs.joinPaths(j.dirs.logDir, 'startupmanager')

    def __init__(self):
        j.logger.logTargetLogForwarder=False
        
        self._configpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'startup')
        j.system.fs.createDir(self._configpath)
        self.processdefs={}
        self.__init=False
        j.system.fs.createDir(StartupManager.LOGDIR)

    def reset(self):
        self.load()
        #kill remainders
        for item in ["byobu","tmux"]:
            cmd="killall %s"%item
            j.system.process.execute(cmd,dieOnNonZeroExitCode=False)

    def _init(self):
        if self.__init==False:
            self.load()
            self.__init=True

    def addProcess(self, name, cmd, args="", env={}, numprocesses=1, priority=100, shell=False,\
        workingdir='',jpackage=None,domain="",ports=[],autostart=True, reload_signal=0,user="root", stopcmd=None, pid=0,\
         active=False,check=True,timeoutcheck=10):
        envstr=""
        for key in env.keys():
            envstr+="%s:%s,"%(key,env[key])
        envstr=envstr.rstrip(",")

        hrd="process.name=%s\n"%name
        if not domain:
            if jpackage:
                domain = jpackage.domain
            else:
                raise RuntimeError("domain should be specified or in jpackage or as argument to addProcess method.")

        hrd+="process.domain=%s\n"%domain
        hrd+="process.cmd=%s\n"%cmd
        if stopcmd:
            hrd+="process.stopcmd=%s\n"%stopcmd
        hrd+="process.args=%s\n"%args
        hrd+="process.env=%s\n"%envstr
        hrd+="process.numprocesses=%s\n"%numprocesses
        hrd+="process.reloadsignal=%s\n"%reload_signal
        hrd+="process.priority=%s\n"%priority
        hrd+="process.workingdir=%s\n"%workingdir
        hrd+="process.user=%s\n"%user
        if autostart:
            autostart=1
        hrd+="process.timeoutcheck=%s\n"%timeoutcheck
        hrd+="process.autostart=%s\n"%autostart
        if check:
            check=1
        else:
            check=0
        hrd+="process.check=%s\n"%check
        pstring=""
        ports = ports[:]
        if jpackage and jpackage.hrd.exists('jp.process.tcpports'):
            for port in jpackage.hrd.getList('jp.process.tcpports'):
                ports.append(port)
        pstring = ",".join( str(x) for x in set(ports) )

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
            self.processdefs[key]=ProcessDef(j.core.hrd.getHRD(path),path=path)

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
        if not processes and (domain or name ):
            raise ProcessNotFoundException("Could not find process with domain:%s and name:%s" % (domain, name))
        return processes

    def exists(self,domain=None,name=None):
        if len(self.getProcessDefs(domain,name))>0:
            return True
        return False

    def getDomains(self):
        result=[]
        for pd in self.processdefs.itervalues():
            if pd.domain not in result:
                result.append(pd.domain)
        return result

    def startJPackage(self,jpackage):
        for pd in self.getProcessDefs4JPackage(jpackage):
            pd.start()

    def stopJPackage(self,jpackage):        
        for pd in self.getProcessDefs4JPackage(jpackage):
            print "stop:%s"%pd
            pd.stop()

    def existsJPackage(self,jpackage):
        return len(self.getProcessDefs4JPackage(jpackage))>0

    def getProcessDefs4JPackage(self,jpackage):
        result=[]
        for pd in self.getProcessDefs():
            if pd.jpackage_name==jpackage.name and pd.jpackage_domain==jpackage.domain:
                result.append(pd)
        return result

    # def _start(self,j,pd):
    #     # print "thread start:%s"%pd
    #     try:
    #         pd.start()
    #     except Exception,e:
    #         print "********** ERROR **********"
    #         print pd
    #         print e
    #         print "********** ERROR **********"
    #     # print "thread started:%s"%pd

    def startAll(self):
        l=self.getProcessDefs()
        for item in l:
            print "will start: %s %s"%(item.priority,item.name)
        
        for pd in self.getProcessDefs():
            # pd.start()
            errors=[]
            
            try:
                pd.start()
            except Exception,e:                
                errors.append("could not start: %s."%pd)
                j.errorconditionhandler.processPythonExceptionObject(e)

        if len(errors)>0:
            print "COULD NOT START:"
            print "\n".join(errors)


    # def startAll(self):
    #     # q = Queue.Queue()
    #     started=[]
    #     for pd in self.getProcessDefs():          
    #         if pd.autostart:
    #             t = threading.Thread(target=self._start, args = (j,pd))
    #             t.daemon = True
    #             started.append(t)
    #             t.start()                  
    #             # pd.start()
    #     while True:
    #         time.sleep(10)
            

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

    def startProcess(self, domain, name):
        for pd in self.getProcessDefs(domain, name):
            pd.start()

    def stopProcess(self, domain,name):
        for pd in self.getProcessDefs(domain, name):
            pd.stop()

    def disableProcess(self, domain,name):
        for pd in self.getProcessDefs(domain, name):
            pd.disable()

    def enableProcess(self, domain,name):
        for pd in self.getProcessDefs(domain, name):
            pd.enable()

    def monitorProcess(self, domain,name):
        for pd in self.getProcessDefs(domain, name):
            pd.monitor()

    def restartProcess(self, domain,name):
        self.stopProcess(domain, name)
        self.startProcess(domain, name)

    def reloadProcess(self, domain, name):
        for pd in self.getProcessDefs(domain, name):
            pd.reload()

