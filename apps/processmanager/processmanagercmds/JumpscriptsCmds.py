from JumpScale import j
import gevent
import copy
import inspect
import imp
import time
import sys
import ujson
from redis import Redis
from rq import Queue

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

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"
        self.osisclient = j.core.osis.getClient(user="root",gevent=True)
        self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript') 

        agentid="%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)

        ipaddr=j.application.config.get("grid.master.ip")        

        self.agentcontroller_client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=self.adminuser , passwd=self.adminpasswd, \
            category="agent",id=agentid,timeout=36000)       



    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        #ASK agentcontroller about known jumpscripts 
        from IPython import embed
        print "DEBUG NOW ASK agentcontroller about known jumpscripts "
        embed()
        
        t=None #@todo

        print "found jumpscript:%s " %("%s_%s" % (organization, name))
        self.jumpscripts["%s_%s" % (organization, name)] = t
        if not self.jumpscriptsByPeriod.has_key(period):
            self.jumpscriptsByPeriod[period]=[]
        self.jumpscriptsByPeriod[period].append(t)

        #@todo remember in redis (NOT NEEDED NOW)
        #self.redis.set("jumpscripts_%s_%s"%(t.organization,t.name),ujson.dumps(t.__dict__))            

        #remember for worker
        tpath=j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts",t.organization,"%s.py"%t.name)

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

