from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.baselib.redisworker
import gevent

REDISIP = '127.0.0.1'
REDISPORT = 7768


class AgentCmds():

    def __init__(self,daemon=None):
        self._name="agent"

        if daemon==None:
            return
            
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth

        self.redis = j.clients.redis.getGeventRedisClient(REDISIP, REDISPORT)

        self.queue={}

        self.queue["io"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:io")
        self.queue["hypervisor"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:hypervisor")
        self.queue["default"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:default")
        
        self.serverip = j.application.config.get('grid.master.ip')
        self.masterport = j.application.config.get('grid.master.port')
        

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"
        self.osisclient = j.core.osis.getClient(ipaddr=self.serverip, port=self.masterport, user="root",gevent=True)
        # self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript') 

        self.client = j.clients.agentcontroller.get(agentControllerIP=self.serverip)

    def _init(self):
        self.init()

    def init(self, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        self._killGreenLets()
        self.daemon.schedule("agent", self.loop)

    def reconnect(self):
        while True:
            try:
                self.client.register()
                return
            except:
                gevent.sleep(5)

    def loop(self):
        """
        fetch work from agentcontroller & put on redis queue
        """
        self.client.register()
        gevent.sleep(2)
        print "start loop to fetch work"
        while True:
            try:
                print "check if work"
                job=self.client.getWork()
                print "check work returns"
                if job<>None:
                    print "WORK FOUND: jobid:%s"%job["id"]
                else:
                    print "no work"
                    continue
            except Exception,e:
                j.errorconditionhandler.processPythonExceptionObject(e)
                self.reconnect()
                continue

            if job["jscriptid"]==None:
                raise RuntimeError("jscript id needs to be filled in")
            j.clients.redisworker.execJobAsync(job)

    def _killGreenLets(self,session=None):
        """
        make sure all running greenlets stop
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        todelete=[]
        for key,greenlet in self.daemon.parentdaemon.greenlets.iteritems():
            if key.find("agent")==0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            self.daemon.parentdaemon.greenlets.pop(key)

