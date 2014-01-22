from JumpScale import j
import gevent
import copy
import inspect
import imp
import time
import sys

from redis import Redis
from rq import Queue

class Jumpscript():

    def __init__(self, name,organization, author, license, version, action, source, path, descr,category,period,startatboot):
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
        self.startatboot=startatboot
        self.lastrun=0
        self.queue="default"
        self.async=False        
        self._name="jumpscripts"

        j.system.fs.createDir(j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts"))
        j.system.fs.writeFile(filename=j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts","__init__.py"),contents="")
        

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

        self.redis = Redis("127.0.0.1", 7768, password=None)

        self.q_i = Queue(name="io",connection=self.redis)
        self.q_h = Queue(name="hypervisor",connection=self.redis)
        self.q_d = Queue(name="default",connection=self.redis)


    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for path2 in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            try:
                fname="%s_%s"%(j.system.fs.getParentDirName(j.system.fs.getDirName(path2)),j.system.fs.getBaseName(path2).replace(".py",""))                
                script = imp.load_source('jumpscript_pm_%s' % fname, path2)
            except Exception as e:
                msg="Could not load jumpscript:%s\n" % path2
                msg+="Error was:%s\n" % e
                # print msg
                j.errorconditionhandler.raiseInputError(msgpub="",message=msg,category="agentcontroller.load",tags="",die=False)
                j.application.stop()
                continue

            name = getattr(script, 'name', "")
            if name=="":
                name=j.system.fs.getBaseName(path2)
                name=name.replace(".py","").lower()
            category = getattr(script, 'category', "unknown")
            organization = getattr(script, 'organization', "unknown")
            author = getattr(script, 'author', "unknown")
            license = getattr(script, 'license', "unknown")
            version = getattr(script, 'version', "1.0")
            enable = getattr(script, 'enable', True)
            order = getattr(script, 'order', 1)
            period = getattr(script, 'period')
            startatboot = getattr(script, 'startatboot',True)
            async = getattr(script, 'async',False)
            queue = getattr(script, 'queue',"default")

            source = inspect.getsource(script.action)

            t = Jumpscript(name, organization, author, license, version, script.action, source, path2, script.descr, category, period,startatboot)
            t.enable = enable
            t.order = order
            t.queue=queue
            t.async=async

            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            self.jumpscripts["%s_%s" % (organization, name)] = t
            if not self.jumpscriptsByPeriod.has_key(period):
                self.jumpscriptsByPeriod[period]=[]
            self.jumpscriptsByPeriod[period].append(t)

            #remember for worker
            tpath=j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts","%s.py"%t.name)
            content="""
from JumpScale import j
"""
            content+=t.source
            j.system.fs.writeFile(filename=tpath,contents=content)

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

    def run(self,period=None):
        if period==None:
            for period in j.processmanager.jumpscripts.jumpscriptsByPeriod.keys():
                self.run(period)

        for action in j.processmanager.jumpscripts.jumpscriptsByPeriod[period]:
            if not action.enable:
                continue
            #print "start action:%s"%action
            if action.lastrun==0 and action.startatboot==False:
                print "did not start at boot:%s"%action.name
            else:
                if action.async==False:
                    try:
                        action.action()
                    except Exception,e:
                        eco=j.errorconditionhandler.parsePythonErrorObject(e)
                        eco.errormessage='Exec error procmgr jumpscr:%s_%s on node:%s_%s %s'%(action.organization,action.name, \
                                j.application.whoAmI.gid, j.application.whoAmI.nid,eco.errormessage)
                        eco.tags="jscategory:%s"%action.category
                        eco.tags+=" jsorganization:%s"%action.organization
                        eco.tags+=" jsname:%s"%action.name                        
                        j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
                else:                    
                    result = self.q_d.enqueue('%s.action'%action.name)
                
            action.lastrun=time.time()
            print "ok:%s"%action.name


    def loop(self, period):
        while True:
            self.run(period)
            gevent.sleep(period) 

    def _configureScheduling(self):        
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)
            self.daemon.schedule("loop%s"%period, self.loop, period=period)

