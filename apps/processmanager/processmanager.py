#!/usr/bin/env python
from JumpScale import j

import JumpScale.grid.geventws
import gevent
from gevent.event import Event
# import JumpScale.baselib.statmanager
import JumpScale.baselib.graphite
import psutil

import JumpScale.baselib.stataggregator

j.application.start("jsprocess_manager")

j.logger.consoleloglevel = 5

class Jumpscript():

    def __init__(self, name,organization, author, license, version, action, source, path, descr,category,period):
        self.name = name
        self.descr = descr
        self.category = category
        self.organization = organization
        self.author = author
        self.license = license
        self.version = version 
        self.source = source
        self.path = path
        self.action=action
        self.category=category
        self.period=period

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__

class MgrCmds():

    def __init__(self, daemon):
        self.daemon = daemon
        self.manager= j.tools.startupmanager
        self.monitorProcess()
        self.lastMonitorResult=None
        self.lastMonitorTime=None
        self.aggregator=j.system.stataggregator
        self.jumpscriptsByPeriod={}
        self.jumpscripts={}
        self.adminpasswd = j.application.config.get('system.superadmin.passwd')
        self.adminuser = j.application.config.get('system.superadmin.login')


    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")           

    def getDomains(self,**args):
        return self.manager.getDomains()

    def listJPackages(self, domain=None, **args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        if not domain:
            packages = j.packages.getInstalledPackages()
        else:
             dobj = j.packages.getDomainObject(domain)
             packages = dobj.getJPackages()
        result = list()
        fields = ('name', 'domain', 'version')
        for package in packages:
            if package.isInstalled():
                pdict = dict()
                for field in fields:
                    pdict[field] = getattr(package, field)
                result.append(pdict)
        return result

    def getJPackage(self, domain, name, **args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        package = j.packages.findNewest(domain, name, returnNoneIfNotFound=True)
        result = dict()
        fields = ('buildNr', 'debug', 'dependencies','domain',
                  'name', 'startupTime', 'supportedPlatforms',
                  'taskletsChecksum', 'tcpPorts', 'version')
        if package:
            for field in fields:
                result[field] = getattr(package, field)
        return result

    def startJPackage(self,jpackage,timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startJPackage(jpackage,timeout)

    def stopJPackage(self,jpackage,timeout=20,**args):  
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.stopJPackage(jpackage,timeout)

    def existsJPackage(self,jpackage,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.existsJPackage(jpackage)

    def startAll(self,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startAll()

    def removeProcess(self,domain, name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.removeProcess(domain, name)

    def getStatus4JPackage(self,jpackage,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.getStatus4JPackage(jpackage)

    def getStatus(self, domain, name,**args):
        """
        get status of process, True if status ok
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.getStatus( domain, name)

    def listProcesses(self,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return [item.split("__") for item in self.manager.listProcesses()]

    def getProcessesActive(self, domain=None, name=None, **kwargs):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        result = list()
        for pd in self.manager.getProcessDefs(domain, name):
            item = dict()
            item['status'] = pd.isRunning()
            item['pid'] = pd.pid
            item['name'] = pd.name
            item['domain'] = pd.domain
            item['autostart'] = pd.autostart == '1'
            item['cmd'] = pd.cmd
            item['args'] = pd.args
            item['args'] = pd.args
            item['ports'] = pd.ports
            item['priority'] = pd.priority
            item['workingdir'] = pd.workingdir
            item['env'] = pd.env
            result.append(item)
        return result


    def startProcess(self, domain="", name="", timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.startProcess( domain, name, timeout)

    def stopProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.stopProcess(domain,name, timeout)

    def disableProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.disableProcess( domain,name, timeout)

    def enableProcess(self, domain,name, timeout=20,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        return self.manager.enableProcess( domain,name, timeout)

    def monitorProcess(self, domain="",name="",remember=False,**args):
        results={}
        for pd in self.manager.getProcessDefs(domain,name):
            t=pd.getStatInfo()
            t2={}
            for key in t.keys():
                results["processes.%s.%s.%s"%(pd.domain,pd.name,key)]=t[key]

        result2={}
        for key in results.keys():
            result2[key]=j.system.stataggregator.set(key,results[key],remember=remember)

        return result2


    def monitorSystem(self,remember=False,session=None):
        
        results={}
        nr=0
        for val in psutil.cpu_percent(0,True):
            nr+=1
            results["cpu.percent.%s"%nr]=round(val,0)

        nr=0
        for cput in psutil.cpu_times(True):
            nr+=1
            for key in cput.__dict__.keys():
                val=cput.__dict__[key]
                results["cpu.time.%s.%s"%(key,nr)]=val

        #disk counters
        counters=psutil.disk_io_counters(True)
        nr=0
        for counterkey in counters.keys():
            counter=counters[counterkey]
            nr+=1
            read_count, write_count, read_bytes, write_bytes, read_time, write_time=counter
            results["disk.time.read.%s"%(counterkey)]=read_time
            results["disk.time.write.%s"%(counterkey)]=write_time
            results["disk.count.read.%s"%(counterkey)]=read_count
            results["disk.count.write.%s"%(counterkey)]=write_count
            results["disk.mbytes.read.%s"%(counterkey)]=round(read_bytes/1024/1024,2)
            results["disk.mbytes.write.%s"%(counterkey)]=round(write_bytes/1024/1024,2)

        #network counters
        counters=psutil.network_io_counters(True)
        nr=0
        for counterkey in counters.keys():
            counter=counters[counterkey]
            nr+=1
            bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout=counter
            results["network.kbytes.recv.%s"%(counterkey)]=round(bytes_recv/1024,0)
            results["network.kbytes.send.%s"%(counterkey)]=round(bytes_sent/1024,0)
            results["network.packets.recv.%s"%(counterkey)]=packets_recv
            results["network.packets.send.%s"%(counterkey)]=packets_sent
            results["network.error.in.%s"%(counterkey)]=errin
            results["network.error.out.%s"%(counterkey)]=errout
            results["network.drop.in.%s"%(counterkey)]=dropin
            results["network.drop.out.%s"%(counterkey)]=dropout

        #disk freespace
        for part in psutil.disk_partitions():
            total,used,free,percent=psutil.disk_usage(part.mountpoint)
            results["disk.space.free.%s"%(part.device)]=round(free/1024/1024,2)
            results["disk.space.used.%s"%(part.device)]=round(used/1024/1024,2)
            results["disk.space.percent.%s"%(part.device)]=percent

        total,used,free,percent=psutil.phymem_usage()
        results["memory.free"]=round(free/1024/1024,2)
        results["memory.used"]=round(used/1024/1024,2)
        results["memory.percent"]=percent

        total,used,free,percent,sin,sout=psutil.virtmem_usage()
        results["swap.free"]=round(free/1024/1024,2)
        results["swap.used"]=round(used/1024/1024,2)
        results["swap.percent"]=percent

        result2={}
        for key in results.keys():
            result2[key]=j.system.stataggregator.set(key,results[key],remember=remember)

        return result2


        # out=""
        # keys=result.keys()
        # keys.sort()
        # for key in keys:
        #     out+="%s.%s %s\n"%(jspid,key,result[key])


        # j.system.statmanager.addInfo(monitorinfo)

    def restartProcess(self, domain,name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.restartProcess( domain,name)

    def reloadProcess(self, domain, name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.reloadProcess( domain,name)

    def startProcess(self, domain,name,**args):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        return self.manager.startProcess( domain,name)



 


    ####JUMPSCRIPT RELATED


    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for path2 in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            C = j.system.fs.fileGetContents(path2)
            C2 = ""
            name = j.system.fs.getBaseName(path2)
            organization = "unknown"
            author = "unknown"
            license = "unknown"
            version = "1.0"
            roles = ["*"]
            source = ""

            state = "start"

            for line in C.split("\n"):
                line = line.replace("\t", "    ")
                line = line.rstrip()
                if line.strip() == "":
                    continue
                if line.find("###########") != -1:
                    break
                C2 += "%s\n" % line
                if state == "start" and line.find("def action") == 0:
                    state = "action"
                if state == "action":
                    source += "%s\n" % line

            try:
                #loads all params
                exec(C2)
            except Exception as e:
                msg="Could not load jumpscript:%s\n" % path2
                msg+="Error was:%s\n" % e
                # print msg
                j.errorconditionhandler.raiseInputError(msgpub="",message=msg,category="agentcontroller.load",tags="",die=False)
                continue

            t = Jumpscript(name,  organization, author, license, version, action, source, path2, descr=descr,category=category,period=period)
            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            self.jumpscripts["%s_%s" % (organization, name)] = t
            if not self.jumpscriptsByPeriod.has_key(period):
                self.jumpscriptsByPeriod[period]=[]
            self.jumpscriptsByPeriod[period].append(t)
        self.killGreenLets()       
        self._configureScheduling()
        
    def getJumpScript(self, organization, name, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        key = "%s_%s" % (organization, name)
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)

    def getJumpscriptFromKey(self, jumpscriptkey, session=None):
        if not self.jumpscriptsFromKeys.has_key(jumpscriptkey):
            message="Could not find jumpscript with key:%s"%jumpscriptkey
            # j.errorconditionhandler.raiseBug(message="Could not find jumpscript with key:%s"%jumpscriptkey,category="jumpscript.controller.scriptnotfound")
            raise RuntimeError(message)
        return self.jumpscriptsFromKeys[jumpscriptkey]

    def listJumpScripts(self, organization=None, cat=None, session=None):
        """
        @return [[org,name,category,descr],...]
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        def myfilter(entry):
            if organization and entry.organization != organization:
                return False
            if cat and entry.category != cat:
                return False
            return True
        return [[t.organization, t.name, t.category, t.descr] for t in filter(myfilter, self.jumpscripts.values()) ]


    def killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        for key,greenlet in self.daemon.parentdaemon.greenlets.iteritems():
            greenlet.kill()     

    def _configureScheduling(self):
        j.processmanager=self
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)

            C="""
def loop_$period():
    while True:
        for action in j.processmanager.jumpscriptsByPeriod[$period]:
            print "start action:%s"%action
            try:
                action.action()
            except Exception,e:
                eco=j.errorconditionhandler.parsePythonErrorObject(e)
                eco.errormessage+='\\n'
                for key in action.__dict__.keys():
                    if key not in ["license"]:
                        eco.errormessage+="%s:%s\\n"%(key,action.__dict__[key]) 
                eco.tags="category:%s"%action.category
                print eco
                j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
                continue
            print "ok"
        gevent.sleep($period) 
"""

            C=C.replace("$period",str(period))
            print C
            exec(C)
            CC="loop_$period"
            CC=CC.replace("$period",str(period))
            
            loopmethod=eval(CC)
            
            self.daemon.schedule("loop%s"%period,loopmethod)


daemon = j.servers.geventws.getServer(port=4445)

daemon.addCMDsInterface(MgrCmds, category="processmanager")  # pass as class not as object !!! chose category if only 1 then can leave ""

cmds=daemon.daemon.cmdsInterfaces["processmanager"][0]
cmds.daemon.schedule=daemon.schedule
cmds.daemon.parentdaemon=daemon
cmds.loadJumpscripts()

daemon.start()

j.application.stop()
