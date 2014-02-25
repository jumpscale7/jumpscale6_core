from JumpScale import j
import gevent
import copy
import inspect
import imp
import time
import sys
import ujson
from redis import Redis
# from rq import Queue
import JumpScale.baselib.redisworker


class JumpScript(object):
    def __init__(self, ddict):
        self.period = 0
        self.lastrun = 0
        self.startatboot = False
        self.__dict__.update(ddict)
        self.write()
        self.load()

    def write(self):
        jscriptdir = j.system.fs.joinPaths(j.dirs.varDir,"jumpscripts", self.organization)
        j.system.fs.createDir(jscriptdir)
        self.path=j.system.fs.joinPaths(jscriptdir, "%s.py" % self.name)

        content="""
from JumpScale import j

"""
        content += self.source
        j.system.fs.writeFile(filename=self.path, contents=content)

    def load(self):
        md5sum = j.tools.hash.md5_string(self.path)
        self.module = imp.load_source('JumpScale.jumpscript_%s' % md5sum, self.path)

    def run(self, *args, **kwargs):
        return self.module.action(*args, **kwargs)

    def execute(self):
        if not self.enable:
            return
        if not self.async:
            try:
                self.run()
            except Exception,e:
                eco=j.errorconditionhandler.parsePythonErrorObject(e)
                eco.errormessage='Exec error procmgr jumpscr:%s_%s on node:%s_%s %s'%(self.organization,self.name, \
                        j.application.whoAmI.gid, j.application.whoAmI.nid,eco.errormessage)
                eco.tags="jscategory:%s"%self.category
                eco.tags+=" jsorganization:%s"%self.organization
                eco.tags+=" jsname:%s"%self.name
                j.errorconditionhandler.raiseOperationalCritical(eco=eco,die=False)
        else:
            # self.q_d.enqueue('%s_%s.action'%(action.organization,action.name))
            #NO LONGER USE redisq, now use our own queuing mechanism
            j.clients.redisworker.execJumpscript(self.id,_timeout=60,_queue="default",_log=True,_sync=False)

        self.lastrun = time.time()
        print "ok:%s"%self.name


class JumpscriptsCmds():

    def __init__(self,daemon=None):
        self._name="jumpscripts"

        if daemon==None:
            return

        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self.jumpscriptsByPeriod={}
        self.jumpscripts={}
        self.aggregator=j.system.stataggregator

        # self.lastMonitorResult=None
        self.lastMonitorTime=None

        self.redis = Redis("127.0.0.1", 7768, password=None)

        # self.q_i = Queue(name="io",connection=self.redis)
        # self.q_h = Queue(name="hypervisor",connection=self.redis)
        # self.q_d = Queue(name="default",connection=self.redis)

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"
        self.osisclient = j.core.osis.getClient(user="root",gevent=True)
        self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript') 

        agentid="%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)

        ipaddr=j.application.config.get("grid.master.ip")        

        self.agentcontroller_client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=self.adminuser , passwd=self.adminpasswd, \
            category="agent",id=agentid,timeout=36000)       


    def _init(self):
        self.loadJumpscripts()

    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        #ASK agentcontroller about known jumpscripts 
        startatboot = list()
        jumpscripts = self.agentcontroller_client.listJumpScripts()
        for jsid,organization, name, category, descr in jumpscripts:
            jumpscript_data=self.agentcontroller_client.getJumpScript(organization, name)
            if jumpscript_data=="":
                raise RuntimeError("Cannot find jumpscript %s %s"%(organization,name))
            jumpscript = JumpScript(jumpscript_data)

            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            # self.jumpscripts["%s_%s" % (organization, name)] = jumpscript
            period = jumpscript.period
            if period:
                if period and period not in self.jumpscriptsByPeriod:
                    self.jumpscriptsByPeriod[period]=[]
                self.jumpscriptsByPeriod[period].append(jumpscript)

            if jumpscript.startatboot:
                startatboot.append(jumpscript)

            self.redis.hset("workers:jumpscripts:id",jumpscript.id, ujson.dumps(jumpscript_data))

            if jumpscript.organization<>"" and jumpscript.name<>"":
                self.redis.hset("workers:jumpscripts:name","%s__%s"%(jumpscript.organization,jumpscript.name), ujson.dumps(jumpscript_data))

        self._killGreenLets()
        self._configureScheduling()
        self._startAtBoot(startatboot)

    ####SCHEDULING###
    def _killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)        
        todelete=[]
        for key,greenlet in self.daemon.parentdaemon.greenlets.iteritems():
            if key.find("loop")==0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            self.daemon.parentdaemon.greenlets.pop(key)

    def _startAtBoot(self, jumpscripts):
        for jumpscript in jumpscripts:
            jumpscript.execute()

    def _run(self,period=None):
        if period==None:
            for period in j.processmanager.jumpscripts.jumpscriptsByPeriod.keys():
                self._run(period)

        for action in j.processmanager.jumpscripts.jumpscriptsByPeriod[period]:
            action.execute()


    def _loop(self, period):
        while True:
            self._run(period)
            gevent.sleep(period)

    def _configureScheduling(self):
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)
            self.daemon.schedule("loop%s"%period, self._loop, period=period)
