from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.baselib.redisworker
import gevent
from JumpScale.grid.serverbase import returnCodes

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
        self.queue["monitoring"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:monitoring")
        
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
        j.core.processmanager.daemon.schedule("agent", self.loop)

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

            if job["queue"]=="internal":
                #cmd needs to be executed internally (is for proxy functionality)
                if self.daemon.cmdsInterfaces.has_key(job["category"]):
                    job["resultcode"],returnformat,job["result"]=self.daemon.processRPC(job["cmd"], data=job["args"], returnformat="m", session=None, category=job["category"])
                    if job["resultcode"]==returnCodes.OK:
                        job["state"]="OK"
                    else:
                        job["state"]="ERROR"
                else:
                    job["resultcode"]=returnCodes.METHOD_NOT_FOUND
                    job["state"]="ERROR"
                    job["result"]="Could not find cmd category:%s"%job["category"]
                self.client.notifyWorkCompleted(job)
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

        for key,greenlet in j.core.processmanager.daemon.greenlets.iteritems():
            if key.find("agent")==0:
                greenlet.kill()
                todelete.append(key)
        for key in todelete:
            j.core.processmanager.daemon.greenlets.pop(key)

    def checkRedisStatus(self, session=None):
        notrunning = list()
        for redisinstance in ['redisac', 'redisp', 'redisc']:
            if not j.clients.redis.getProcessPids(redisinstance):
                notrunning.append(redisinstance)
        if not notrunning:
            return True
        return notrunning

    def checkRedisSize(self, session=None):
        redisinfo = j.clients.redisworker.redis.info().split('\r\n')
        info = dict()
        for entry in redisinfo:
            if ':' in entry:
                key, value = entry.split(':')
                info[key] = value
        size = info['used_memory']
        maxsize = 50 * 1024 * 1024
        if j.basetype.float.fromString(size) < maxsize:
            return True
        return False




