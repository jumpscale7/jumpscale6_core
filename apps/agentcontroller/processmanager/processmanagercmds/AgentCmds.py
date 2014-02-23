from JumpScale import j
import JumpScale.grid.agentcontroller
import ujson
import JumpScale.baselib.redisworker

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

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"
        self.osisclient = j.core.osis.getClient(user="root",gevent=True)
        # self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript') 

        self.client = j.clients.agentcontroller.get()

    def _init(self):
        self.init()

    def init(self, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        self._killGreenLets()
        self.daemon.schedule("agent", self.loop)


    def loop(self):
        """
        fetch work from agentcontroller & put on redis queue
        """
        self.client.register()

        while True:

            ok=False
            while ok==False:
                try:
                    # print "check if work"
                    job=self.client.getWork()
                    ok=True
                except Exception,e:
                    # self.register()
                    continue

            if not job:
                print 'no work here'

            if job and ok:
                # jscriptid = "%s_%s" % (job["category"], job["cmd"])

                j.clients.redisworker.execJumpscript(jumpscriptid=job["jscriptid"],jumpscript=None,_timeout=60,_queue=job["queue"],_log=True,_sync=False,**job["args"])

                # qname=job["queue"]
                # if not qname or qname.strip()=="":
                #     qname="default"

                # if not self.queue.has_key(qname):
                #     raise RuntimeError("Could not find queue to execute job:%s ((ops:processmanager.agent.schedulework L:1))"%job)

                # queue=self.queue[qname]

                # # result = queue.enqueue_call('%s_%s.action'%(job["category"],job["cmd"]),kwargs=job["args"],\
                # #     timeout=int(job["timeout"]))
                # self.redis.hset("workerjobs",job["id"], ujson.dumps(job))
                # queue.put(job["id"])
                # #need to do something here to make sure they are both in redis #@todo P1

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

