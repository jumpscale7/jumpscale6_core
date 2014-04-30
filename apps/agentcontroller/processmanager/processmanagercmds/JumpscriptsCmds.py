from JumpScale import j
import gevent
import ujson
from redis import Redis
# from rq import Queue
import JumpScale.baselib.redisworker
from JumpScale.grid.processmanager.ProcessmanagerFactory import JumpScript

class JumpscriptsCmds():
    ORDER = 20

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
                
        self.masterport = j.application.config.get('grid.master.port')
        self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.daemon.osis, 'system', 'jumpscript') 

    def _init(self):
        self.loadJumpscripts()

    def loadJumpscripts(self, path="jumpscripts", session=None):
        print "LOAD JUMPSCRIPTS"
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        agentid="%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)
        ipaddr=j.application.config.get("grid.master.ip")

        self.agentcontroller_client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=self.adminuser , passwd=self.adminpasswd, \
            category="agent",id=agentid,timeout=60)       

        self.jumpscriptsByPeriod={}
        self.jumpscripts={}

        jspath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'processmanager', 'jumpscripts')
        if j.system.fs.exists(jspath):
            startatboot = self._loadFromPath(jspath)
        else:
            startatboot = self._loadFromAC()

        self._killGreenLets()
        self._configureScheduling()
        self._startAtBoot(startatboot)
        return "ok"

    def _loadFromPath(self, path):
        startatboot = list()
        jumpscripts = self.agentcontroller_client.listJumpScripts()
        iddict = { (org, name): jsid for jsid, org, name, _,_ in jumpscripts }
        for jscriptpath in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            js = JumpScript(path=jscriptpath)
            js.id = iddict[(js.organization, js.name)]
            self._processJumpScript(js, startatboot)
        return startatboot

    def _loadFromAC(self):
        startatboot = list()
        jumpscripts = self.agentcontroller_client.listJumpScripts()
        for jsid,organization, name, category, descr in jumpscripts:
            jumpscript_data=self.agentcontroller_client.getJumpScript(organization, name)
            if jumpscript_data=="":
                raise RuntimeError("Cannot find jumpscript %s %s"%(organization,name))
            jumpscript = JumpScript(jumpscript_data)
            self._processJumpScript(jumpscript, startatboot)
        return startatboot

    def _processJumpScript(self, jumpscript, startatboot):
        roles = set(j.core.grid.roles)
        if jumpscript.enable and roles.issuperset(set(jumpscript.roles)):
            organization = jumpscript.organization
            name = jumpscript.name
            self.jumpscripts["%s_%s"%(organization,name)]=jumpscript

            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            # self.jumpscripts["%s_%s" % (organization, name)] = jumpscript
            period = jumpscript.period
            if period<>None:
                period=int(period)
                if period>0:
                    if period not in self.jumpscriptsByPeriod:
                        self.jumpscriptsByPeriod[period]=[]
                    print "schedule jumpscript %s on period:%s"%(jumpscript.name,period)
                    self.jumpscriptsByPeriod[period].append(jumpscript)

            if jumpscript.startatboot:
                startatboot.append(jumpscript)

            self.redis.hset("workers:jumpscripts:id",jumpscript.id, ujson.dumps(jumpscript.getDict()))

            if jumpscript.organization<>"" and jumpscript.name<>"":
                self.redis.hset("workers:jumpscripts:name","%s__%s"%(jumpscript.organization,jumpscript.name), ujson.dumps(jumpscript.getDict()))

    ####SCHEDULING###

    def _killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        todelete=[]

        for key,greenlet in j.core.processmanager.daemon.greenlets.iteritems():
            if key.find("loop")==0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            j.core.processmanager.daemon.greenlets.pop(key)            

    def _startAtBoot(self, jumpscripts):
        for jumpscript in jumpscripts:
            jumpscript.execute()

    def _run(self,period=None):
        
        if period==None:
            for period in j.core.processmanager.cmds.jumpscripts.jumpscriptsByPeriod.keys():
                self._run(period)

        if j.core.processmanager.cmds.jumpscripts.jumpscriptsByPeriod.has_key(period):
            for action in j.core.processmanager.cmds.jumpscripts.jumpscriptsByPeriod[period]:
                # print "execute:%s"%action.name
                action.execute()

    def _loop(self, period):
        while True:
            self._run(period)
            gevent.sleep(period)

    def _configureScheduling(self):
        for period in self.jumpscriptsByPeriod.keys():
            period=int(period)
            j.core.processmanager.daemon.schedule("loop%s"%period, self._loop, period=period)
