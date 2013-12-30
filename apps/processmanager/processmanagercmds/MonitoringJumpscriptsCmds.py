from JumpScale import j
import gevent

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
        self.order=1
        self.enable=True

    def __repr__(self):
        return "%s %s"%(self.name,self.descr)

    __str__ = __repr__


class MonitoringJumpscriptsCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.jumpscriptsByPeriod={}
        self.jumpscripts={}
        self.aggregator=j.system.stataggregator
        self._name="jumpscripts"

        # self.lastMonitorResult=None
        self.lastMonitorTime=None

    def loadMonitoringJumpscripts(self, path="monitoringjumpscripts", session=None):
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

            enable=True
            order=1

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
            t.order=order
            t.enable=enable
            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            self.jumpscripts["%s_%s" % (organization, name)] = t
            if not self.jumpscriptsByPeriod.has_key(period):
                self.jumpscriptsByPeriod[period]=[]
            self.jumpscriptsByPeriod[period].append(t)
        self.killGreenLets()       
        self._configureScheduling()
        
    def getMonitoringJumpscript(self, organization, name, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        key = "%s_%s" % (organization, name)
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)

    def getMonitoringJumpscriptFromKey(self, jumpscriptkey, session=None):
        if not self.jumpscriptsFromKeys.has_key(jumpscriptkey):
            message="Could not find jumpscript with key:%s"%jumpscriptkey
            # j.errorconditionhandler.raiseBug(message="Could not find jumpscript with key:%s"%jumpscriptkey,category="jumpscript.controller.scriptnotfound")
            raise RuntimeError(message)
        return self.jumpscriptsFromKeys[jumpscriptkey]

    def listMonitoringJumpScripts(self, organization=None, cat=None, session=None):
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


    ####SCHEDULING###
    def killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        for key,greenlet in self.daemon.parentdaemon.greenlets.iteritems():
            greenlet.kill()     

    def _configureScheduling(self):        
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)

            C="""
def loop_$period():
    while True:
        for action in j.processmanager.jumpscripts.jumpscriptsByPeriod[$period]:
            if not action.enable:
                continue
            #print "start action:%s"%action
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
            # print C
            exec(C)
            CC="loop_$period"
            CC=CC.replace("$period",str(period))
            
            loopmethod=eval(CC)
            
            self.daemon.schedule("loop%s"%period,loopmethod)

