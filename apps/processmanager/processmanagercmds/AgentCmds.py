from JumpScale import j
import gevent
import copy
import inspect
import imp
import time
import sys
import ujson


class AgentCmds():

    def __init__(self,daemon):
        self.daemon=daemon
        self._adminAuth=daemon._adminAuth
        self._name="agent"

        self.redis = Redis("127.0.0.1", 7768, password=None)

        self.queue={}

        # self.queue["io"] = Queue(name="io",connection=self.redis)
        # self.queue["hypervisor"] = Queue(name="hypervisor",connection=self.redis)
        # self.queue["default"] = Queue(name="default",connection=self.redis)

        #@todo use geventqueues
        self.queue["io"] = j.clients.redis.getRedisQueue("127.0.0.1",7768,"workers:work:io")
        self.queue["hypervisor"] = j.clients.redis.getRedisQueue("127.0.0.1",7768,"workers:work:hypervisor")
        self.queue["default"] = j.clients.redis.getRedisQueue("127.0.0.1",7768,"workers:work:default")

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"
        self.osisclient = j.core.osis.getClient(user="root",gevent=True)
        # self.osis_jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript') 

        agentid="%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid)

        ipaddr=j.application.config.get("grid.master.ip")        

        self.agentcontroller_client = j.servers.geventws.getClient(ipaddr, 4444, org="myorg", user=self.adminuser , passwd=self.adminpasswd, \
            category="agent",id=agentid,timeout=36000)       

    def init(self, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        self._killGreenLets()       
        self.daemon.schedule("agent", self.loop)


    def loop(self):
        """
        fetch work from agentcontroller & put on redis queue
        """
        while True:

            ok=False
            while ok==False:
                try:
                    # print "check if work"
                    job=self.agentcontroller_client.getWork()
                    ok=True
                except Exception,e:
                    # self.register()
                    continue

            if not job:
                print 'no work here'
                
            if job and ok:
                # jscriptid = "%s_%s" % (job["category"], job["cmd"])

                qname=job["queue"]
                if qname.strip()=="":
                    qname="default"

                if not self.queue.has_key(qname):
                    raise RuntimeError("Could not find queue to execute job:%s ((ops:processmanager.agent.schedulework L:1))"%job)

                queue=self.queue[qname]

                # result = queue.enqueue_call('%s_%s.action'%(job["category"],job["cmd"]),kwargs=job["args"],\
                #     timeout=int(job["timeout"]))
                
                self.redis.hset("workerjobs",job["id"], ujson.dumps(job))
                queue.put(job["id"])
                #need to do something here to make sure they are both in redis #@todo P1

                
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

            

