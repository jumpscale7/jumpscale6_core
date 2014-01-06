from JumpScale import j
import gevent
import copy
import inspect
import imp
import functools

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
        self._name="jumpscripts"

    def __repr__(self):
        return "%s %s"%(self.name,self.descr)

    __str__ = __repr__


class JumpscriptsCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.jumpscriptsByPeriod={}
        self.jumpscripts={}
        self.aggregator=j.system.stataggregator
        self._name="jumpscripts"

        # self.lastMonitorResult=None
        self.lastMonitorTime=None

    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for path2 in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            try:
                script = imp.load_source('jumpscript.%s' % j.tools.hash.md5_string(path2), path2)
            except Exception as e:
                msg="Could not load jumpscript:%s\n" % path2
                msg+="Error was:%s\n" % e
                # print msg
                j.errorconditionhandler.raiseInputError(msgpub="",message=msg,category="agentcontroller.load",tags="",die=False)
                continue

            name = getattr(script, 'name', "")
            category = getattr(script, 'category', "unknown")
            organization = getattr(script, 'organization', "unknown")
            author = getattr(script, 'author', "unknown")
            license = getattr(script, 'license', "unknown")
            version = getattr(script, 'version', "1.0")
            enable = getattr(script, 'enable', True)
            order = getattr(script, 'order', 1)
            period = getattr(script, 'period')
            source = inspect.getsource(script.action)

            t = Jumpscript(name, organization, author, license, version, script.action, source, path2, script.descr, category, period)
            t.enable = enable
            t.order = order
            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            self.jumpscripts["%s_%s" % (organization, name)] = t
            if not self.jumpscriptsByPeriod.has_key(period):
                self.jumpscriptsByPeriod[period]=[]
            self.jumpscriptsByPeriod[period].append(t)
        self._killGreenLets()       
        self._configureScheduling()
        
    def getJumpscript(self, organization, name, session=None):

        if session<>None:
            self._adminAuth(session.user,session.passwd)
        key = "%s_%s" % (organization, name)
        if key in self.jumpscripts.keys():              
            r=copy.copy(self.jumpscripts[key].__dict__)
            r.pop("action")
            return r            
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), \
                category="action.notfound", die=True)

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


    ####SCHEDULING###
    def _killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        for key,greenlet in self.daemon.parentdaemon.greenlets.iteritems():
            greenlet.kill()

    def loop(self, period):
        while True:
            for action in j.processmanager.jumpscripts.jumpscriptsByPeriod[period]:
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
                    j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
                    continue
                print "ok"
            gevent.sleep(period) 

    def _configureScheduling(self):        
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)
            loopmethod = functools.partial(self.loop, period)
            self.daemon.schedule("loop%s"%period, loopmethod)

