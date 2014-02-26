
from JumpScale import j
import JumpScale.grid.geventws
import gevent
import gevent.coros
import JumpScale.grid.osis
import imp
import importlib
import inspect
import ujson as json

j.application.start("jumpscale:agentcontroller")
j.application.initGrid()

j.logger.consoleloglevel = 2
import JumpScale.baselib.redis

#check redis is there if not try to start
if not j.system.net.tcpPortConnectionTest("127.0.0.1",7769):
    raise RuntimeError("did not find redis on port %s"%7769)

class ControllerCMDS():

    def __init__(self, daemon):
        self.debug = False # set true for verbose output

        j.application.initGrid()

        self.daemon = daemon
        self.jumpscripts = {}
        self.jumpscriptsFromKeys = {}
        self.jumpscriptsId={}

        self.roles2agents = {}  # key=role in all depths
        self.agentqueues = dict()
        self.sessionsUpdateTime={}

        # self.session2agent={} #key= sessionid, val = agentid
        # self.agent2sessions={} #key=agent, val=list of sessions
        # self.sessions={} #key=sessionid
        # self.sessionsUpdateTime={} #key=sessionid, val is last epoch of contact
        # self.activeJobSessions={}  # key=sessionid , is job running per session or does not exist if no job running on that session

        # self.agent2freeSessions={} #key is agent, val is dict of sessions free to be used

        self.adminpasswd = j.application.config.get('grid.master.superadminpasswd')
        self.adminuser = "root"

        self.osisclient = j.core.osis.getClient(user=self.adminuser,gevent=True)
        self.jobclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'job')
        self.nodeclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'node')
        self.jumpscriptclient = j.core.osis.getClientForCategory(self.osisclient, 'system', 'jumpscript')

        self.redisport=7769
        self.redis = j.clients.redis.getGeventRedisClient("127.0.0.1", self.redisport)

        j.logger.setLogTargetLogForwarder()

    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")

    def authenticate(self, session):
        return False  # to make sure we dont use it

    def scheduleCmd(self,gid,nid,cmdcategory,cmdname,args={},jscriptid=None,queue="",log=True,timeout=0,roles=[],session=None): 
        """ 
        new preferred method for scheduling work
        @name is name of cmdserver method or name of jumpscript 
        """
        self._log("schedule cmd:%s_%s %s %s"%(gid,nid,cmdcategory,cmdname))
        if session<>None: 
            self._adminAuth(session.user,session.passwd) 
        self._log("getjob osis client")
        job=self.jobclient.new(sessionid=session.id,gid=gid,nid=nid,category=cmdcategory,cmd=cmdname,queue=queue,args=args,log=log,timeout=timeout,roles=roles) 
        self._log("redis incr for job")
        jobid=self.redis.hincrby("jobs:last",str(session.gid),1) 
        self._log("jobid found (incr done)")
        job.id=jobid
        job.getSetGuid()
        if not jscriptid:
            action = self.getJumpScript(cmdcategory, cmdname, session=session)
            jscriptid = action.id
        job.jscriptid = jscriptid
        jobs=json.dumps(job)
        self._log("save 2 osis")
        self._setJob(job.__dict__, True,jobs)
        self._log("getqueue")
        q = self._getCmdQueue(gid=gid, nid=nid)
        self._log("put on queue")
        q.put(jobs)
        self._log("schedule done")
        return job.__dict__

    def _setJob(self, job, osis=False,jobs=None):
        if not j.basetype.dictionary.check(job):
            raise RuntimeError("job needs to be dict")  
        if jobs==None:
            jobs=json.dumps(job)
        self.redis.hset("jobs:%s"%job["gid"],job["id"],jobs)
        if osis:
            # we need to make sure that job['resul'] is always of the same type hence we serialize
            # otherwise elasticsearch will have issues
            if 'result' in job:
                job['result'] = json.dumps(job['result'])
            self.jobclient.set(job)

    def _getJobFromRedis(self, gid, jobid):
        jobdict = json.loads(self.redis.hget("jobs:%s"%gid, jobid))
        return jobdict
        # return self.jobclient.new(ddict=jobdict)

    def _getCmdQueue(self, session=None, gid=None, nid=None):
        """
        is qeueue where commands are scheduled for processmanager to be picked up
        """
        if not gid and not nid:
            gid = session.gid
            nid = session.nid
        if session==None:
            self._log("get cmd queue NOSESSION")
        self._log("get cmd queue for %s %s"%(gid,nid))
        queuename = "commands:queue:%s:%s" % (gid, nid)
        return j.clients.redis.getGeventRedisQueue("127.0.0.1", self.redisport, queuename, fromcache=True)

    def _getJobQueue(self, jobid):
        queuename = "jobqueue:%s" % jobid
        self._log("get job queue for job:%s"%(jobid))
        return j.clients.redis.getGeventRedisQueue("127.0.0.1", self.redisport, queuename, fromcache=False)
        
    def _setRole2Agent(self,role,agent):
        if not self.roles2agents.has_key(role):
            self.roles2agents[role]=[]
        if agent not in self.roles2agents[role]:
            self.roles2agents[role].append(agent)   

    def register(self,session):
        self._log("new agent:")
        roles=session.roles
        agentid="%s_%s"%(session.gid,session.nid)
        for role in roles:
            self._setRole2Agent(role, agentid)
        self.sessionsUpdateTime[agentid]=j.base.time.getTimeEpoch()
        self._log("register done:%s"%agentid)

    def escalateError(self, eco, session=None):
        if isinstance(eco, dict):
            eco = j.errorconditionhandler.getErrorConditionObject(eco)
        j.errorconditionhandler.processErrorConditionObject(eco)

    def loadJumpscripts(self, path="jumpscripts", session=None):

        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for path2 in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):

            if j.system.fs.getDirName(path2,True)[0]=="_": #skip dirs starting with _
                continue

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

            source = inspect.getsource(script)
            t=self.jumpscriptclient.new(name=name,action=script.action)
            t.name=name
            t.author=getattr(script, 'author', "unknown")
            t.organization=getattr(script, 'organization', "unknown")
            t.category=getattr(script, 'category', "unknown")
            t.license=getattr(script, 'license', "unknown")
            t.version=getattr(script, 'version', "1.0")
            t.roles=getattr(script, 'roles', ["*"])
            t.source=source
            t.path=path2
            t.descr=script.descr
            t.queue=getattr(script, 'queue',"default")
            t.async = getattr(script, 'async',False)
            t.period=getattr(script, 'period',0)
            t.order=getattr(script, 'order', 1)
            t.log=getattr(script, 'log', True)
            t.enable=getattr(script, 'enable', True)
            t.startatboot=getattr(script, 'startatboot', False)
            t.gid=getattr(script, 'gid', j.application.whoAmI.gid)


            guid,r,r=self.jumpscriptclient.set(t)
            t=self.jumpscriptclient.get(guid)
            
            self._log("found jumpscript:%s " %("id:%s %s_%s" % (t.id,t.organization, t.name)))

            key0 = "%s_%s" % (t.gid,t.id)
            key = "%s_%s_%s" % (t.gid,t.organization, t.name)
            self.jumpscripts[key] = t
            self.jumpscriptsId[key0] = t
       
    def getJumpScript(self, organization, name,gid=None, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
            
        if gid==None and session <> None:
            gid = session.gid
        elif id==None and session == None:
            gid=j.application.whoAmI.gid

        key = "%s_%s_%s" % (gid,organization, name)
        
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)
            return ""

    def getJumpScriptFromId(self,id,gid=None,session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        else:
            if gid==None and session <> None:
                gid = session.gid
            elif id==None and session == None:
                gid=j.application.whoAmI.gid

        key = "%s_%s" % (gid,id)
        
        if key in self.jumpscriptsId:
            return self.jumpscriptsId[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s" % (key), category="action.notfound", die=False)

    def existsJumpScript(self, organization, name,gid=None, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
            gid = session.gid
        else:
            if gid==None:
                gid=j.application.whoAmI.gid

        key = "%s_%s_%s" % (gid,organization, name)
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)

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
        return [[t.id,t.organization, t.name, t.category, t.descr] for t in filter(myfilter, self.jumpscripts.values()) ]

    def executeJumpScript(self, organization, name, nid=None, role=None, args={},all=False, timeout=600,wait=True,queue="", session=None):
        """
        @param roles defines which of the agents which need to execute this action
        @all if False will be executed only once by the first found agent, if True will be executed by all matched agents
        """
        def noWork():
            job=self.jobclient.new(sessionid=session.id,gid=0, category=organization,cmd=name,queue=queue,args=args,log=True,timeout=timeout)
            self._log("nothingtodo")
            job.state="NOWORK"
            job.timeStop=job.timeStart
            self._setJob(job.__dict__, osis=True)
            return job.__dict__

        self._adminAuth(session.user,session.passwd)
        self._log("AC:get request to exec JS:%s %s on node:%s"%(organization,name,nid))
        action = self.getJumpScript(organization, name, session=session)
        if action==None:
            raise RuntimeError("Cannot find jumpscript %s %s"%(organization,name))
        if role<>None:
            self._log("ROLE NOT NONE")
            role = role.lower()
            if role in self.roles2agents:
                for agentid in self.roles2agents[role]:
                    gid,nid=agentid.split("_")
                    job=self.scheduleCmd(gid,nid,organization,name,args=args,queue=queue,log=True,timeout=timeout,roles=[role],session=session,jscriptid=action.id)
                if wait:
                    return self.waitJumpscript(job=job,session=session)
                return job
            else:
                return noWork()
        elif nid<>None:
            self._log("NID KNOWN")
            job=self.scheduleCmd(session.gid,nid,organization,name,args=args,queue=queue,log=True,timeout=timeout,session=session,jscriptid=action.id)
            if wait:
                return self.waitJumpscript(job=job,session=session)
            return job
        else:
            return noWork()

    def waitJumpscript(self,jobid=None,job=None,session=None):
        """
        @return job as dict
        """
        if job==None:
            if jobid==None:
                raise RuntimeError("job or jobid need to be given as argument")
            job = self._getJobFromRedis(session.gid, jobid)
        if job['state'] != 'SCHEDULED':
            return job
        q = self._getJobQueue(job["id"])
        if job["timeout"]<>0:
            res = q.fetch(timeout=job["timeout"])
        else:
            res = q.fetch()
        q.set_expire(5)
        if res:
            return json.loads(res)
        else:
            json.loads(job)
            job["resultcode"]=1
            job["state"]="TIMEOUT"
            self._setJob(job, osis=True)
            self._log("timeout on execution")
            return job

    def getWork(self, session=None):
        """
        is for agent to ask for work
        returns job as dict
        """
        self._log("getwork %s" % session)
        q = self._getCmdQueue(session)
        jobstr=q.get(timeout=30)
        if jobstr==None:
            self._log("NO WORK")
            return None
        job=json.loads(jobstr)
        if job<>None:
            self._log("getwork found for node:%s for jsid:%s"%(session.nid,job["jscriptid"]))
            return job


    def notifyWorkCompleted(self, job,session=None):
        """
        job here is a dict
        """
        self._log("NOTIFY WORK COMPLETED: jobid:%s"%job["id"])
        if not j.basetype.dictionary.check(job):
            raise RuntimeError("job needs to be dict")            
        self.sessionsUpdateTime[session.id]=j.base.time.getTimeEpoch()
        self._setJob(job, osis=True)
        q=self._getJobQueue(job["id"])
        q.put(json.dumps(job))

        #NO PARENT SUPPORT YET
        # #now need to return it to the client who asked for the work 
        # if job.parent and job.parent in self.jobs:
        #     parentjob = self.jobs[job.db.parent]
        #     parentjob.db.childrenActive.remove(job.id)
        #     if job.db.state == 'ERROR':
        #         parentjob.db.state = 'ERROR'
        #         parentjob.db.result = job.db.result
        #     if not parentjob.db.childrenActive:
        #         #all children executed
        #         parentjob.db.resultcode=0
        #         if parentjob.db.state != 'ERROR':
        #             parentjob.db.state = "OK"
        #         if not parentjob.db.result:
        #             parentjob.db.result = json.dumps(None)
        #         parentjob.save()
        #         parentjob.done()

        self._log("completed job")
        return

    def getScheduledWork(self,agentid,session=None):
        """
        list all work scheduled for 1 agent
        """
        raise RuntimeError("need to be implemented")
        self._adminAuth(session.user,session.passwd)
        result=[]
        for sessionid in self.agent2session[agentid]:
            if self.workqueue.has_key(sessionid):
                if len(self.workqueue[sessionid])>0:
                    result=[item.__dict__ for item in self.workqueue[sessionid]]
        return result

    def getActiveWork(self,agentid,session=None):
        """
        list all work active for 1 agent
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        raise RuntimeError("need to be implemented")
        result=[]
        if self.workqueue.has_key(session.agentid):
            if len(self.workqueue[session.agentid])>0:
                result=[item.__dict__ for item in self.workqueue[session.agentid]]
        return result

    def log(self, logs, session=None):
        for log in logs:
            j.logger.logTargetLogForwarder.log(log)

    def _log(self, msg):
        if self.debug:
            print msg

    def getProcessmanagerScripts(self, session=None):
        """
        create tar.gz of cmds & monitoring objects & return as binary info
        """
        #@todo make async with local workers
        import tarfile
        ppath="/tmp/processMgrScripts_%s.tar"%j.base.idgenerator.generateRandomInt(1,1000000)
        with tarfile.open(ppath, "w:bz2") as tar:
            for path in j.system.fs.listFilesInDir("processmanager",True):
                if j.system.fs.getFileExtension(path)<>"pyc":
                    tar.add(path)
        data=j.system.fs.fileGetContents(ppath)
        j.system.fs.remove(ppath)
        return data

    def listSessions(self,session=None):
        #result=[]
        #for sessionid, session in self.sessions.iteritems():
        #    sessionresult={}
        #    sessionresult["id"]=sessionid
        #    sessionresult["roles"]=session.roles
        #    sessionresult["netinfo"]=session.netinfo
        #    sessionresult["organization"]=session.organization
        #    sessionresult["agentid"]=session.agentid
        #    sessionresult["id"]=session.id
        #    sessionresult["user"]=session.user
        #    sessionresult["start"]=session.start
        #    sessionresult["lastpoll"]=self.sessionsUpdateTime[session.id]
        #    activejob = self.activeJobSessions.get(session.id)
        #    sessionresult["activejob"] = activejob.id if activejob else None
        #    result.append(sessionresult)
        return self.roles2agents

    def getJobInfo(self, jobid, session=None):
        raise RuntimeError("need to be implemented")
        job = self.jobs.get(jobid)
        if job:
            return job.db.__dict__

    def getActiveJobs(self, session=None):
        raise RuntimeError("need to be implemented")
        results = list()
        for value in self.activeJobSessions.itervalues():
            results.append(value.db.__dict__)
        return results

    def listJobs(self, session=None):
        """
        list all jobs waiting for which roles, show for each role which agents should be answering
        also list jobs which are running and running in which sessions
        """
        raise RuntimeError("need to be implemented")
        result = []
        jobresult = {}

        for jobid in self.jobs.keys():
            job = self.jobs[jobid]
            jobresult['id'] = jobid
            jobresult['jsname'] = job.db.jsname
            jobresult['jsorganization'] = job.db.jsorganization
            jobresult['roles'] = job.db.roles
            # jobresult['args'] = job.db.args
            jobresult['timeout'] = job.db.timeout
            jobresult['result'] = job.db.result
            jobresult['sessionid'] = job.db.sessionid
            jobresult['jscriptid'] = job.db.jscriptid
            jobresult['children'] = job.db.children
            jobresult['childrenActive'] = job.db.childrenActive
            jobresult['parent'] = job.db.parent
            jobresult['resultcode'] = job.db.resultcode
            if self.activeJobSessions.has_key(session.id):
                jobresult["isactive"] == jobid in self.activeJobSessions[session.id]
            else:
                jobresult["isactive"] = False
            result.append(jobresult)
        return result

# will reinit for testing everytime, not really needed
# j.servers.geventws.initSSL4Server("myorg", "controller1")

daemon = j.servers.geventws.getServer(port=4444)

daemon.addCMDsInterface(ControllerCMDS, category="agent")  # pass as class not as object !!! chose category if only 1 then can leave ""

print "load processmanager cmds"
# j.system.fs.changeDir("processmanager")
import sys
sys.path.append(j.system.fs.joinPaths(j.system.fs.getcwd(),"processmanager"))
for item in j.system.fs.listFilesInDir("processmanager/processmanagercmds",filter="*.py"):
    name=j.system.fs.getBaseName(item).replace(".py","")
    if name[0]<>"_":
        module = importlib.import_module('processmanagercmds.%s' % name)
        classs = getattr(module, name)
        tmp=classs()
        daemon.addCMDsInterface(classs, category="processmanager_%s"%tmp._name,proxy=True)

# j.system.fs.changeDir("..")

cmds=daemon.daemon.cmdsInterfaces["agent"][0]
cmds.loadJumpscripts()

daemon.start()


j.application.stop()

