
from JumpScale import j
import JumpScale.grid.geventws
import gevent
from gevent.event import Event
import JumpScale.grid.osis
import imp
import inspect
import ujson as json

j.application.start("jumpscale:agentcontroller")
j.application.initGrid()

j.logger.consoleloglevel = 2
import JumpScale.baselib.redis

class ControllerCMDS():

    def __init__(self, daemon):

        j.application.initGrid()

        self.daemon = daemon
        self.jumpscripts = {}
        self.jumpscriptsFromKeys = {}

        # self.workqueue = {}  # key=agentid

        # self.jobs= {} #key is jobid

        self.roles2agents = {}  # key=role in all depths

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
        
        self.redis = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768)

        j.logger.setLogTargetLogForwarder()


    def _adminAuth(self,user,passwd):
        if user != self.adminuser or passwd != self.adminpasswd:
            raise RuntimeError("permission denied")

    def authenticate(self, session):
        return False  # to make sure we dont use it

    def _setRole2Agent(self,role,agent):
        if not self.roles2agents.has_key(role):
            self.roles2agents[role]=[]
        if agent not in self.roles2agents[role]:
            self.roles2agents[role].append(agent)   


    def register(self,session):

        print "new agent:"
        print session

        # self._clean(similarProcessPIDs,session)
        # self.sessions[session.id]=session
        # self.session2agent[session.id]=session.agentid
        roles=session.roles
        gid,nid=session.agentid.split("_")


        from IPython import embed
        print "DEBUG NOW register"
        embed()
        
        for role in roles:
            self._setRole2Agent(role,session.agentid)
            compl=""
            while role.find(".")<>-1:
                pre,role=role.split(".",1)
                compl+=".%s"%pre
                self._setRole2Agent(compl.lstrip("."),session.agentid)
        self.workqueue[session.agentid]=[]

        #mark agent 2 session
        if not self.agent2sessions.has_key(session.agentid):
            self.agent2sessions[session.agentid]=[]
        if session.id not in self.agent2sessions[session.agentid]:
            self.agent2sessions[session.agentid].append(session.id)

        self.sessionsUpdateTime[session.id]=j.base.time.getTimeEpoch()

        if not self.agent2freeSessions.has_key(session.agentid):
            self.agent2freeSessions[session.agentid]={}

        print "register done:%s"%session.id

    def _markSessionFree(self,session):
        self.agent2freeSessions[session.agentid][session.id]=Event()
        return self.agent2freeSessions[session.agentid][session.id]

    def _unmarkSessionFree(self,session):
        if not self.agent2freeSessions.has_key(session.agentid):
            raise RuntimeError("bug in _unmarkSessionFree in agentcontroller, sessionfree needs to have agentid")

        if self.agent2freeSessions[session.agentid].has_key(session.id):
            self.agent2freeSessions[session.agentid].pop(session.id)

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
            t.enable=getattr(script, 'enable', True)
            t.gid=getattr(script, 'gid', j.application.whoAmI.gid)


            self.jumpscriptclient.set(t)
            print "found jumpscript:%s " %("%s_%s" % (t.organization, t.name))
            # self.jumpscripts["%s_%s_%s" % (t.gid,t.organization, t.name)] = True

            redis = j.clients.redis.getGeventRedisClient('127.0.0.1', 7768, False)
            redis.set("jumpscripts_%s_%s_%s"%(t.gid,t.organization,t.name),json.dumps(t.__dict__))
            key = "%s_%s_%s" % (j.application.whoAmI.gid,t.organization, t.name)
            self.jumpscripts[key] = t

        
    def getJumpScript(self, organization, name,gid=None, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
            gid = session.gid
            nid = session.nid
        else:
            if gid==None:
                gid=j.application.whoAmI.gid

        key = "%s_%s_%s" % (gid,organization, name)
        
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)

    def existsJumpScript(self, organization, name,gid=None, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
            gid = session.gid
            nid = session.nid
        else:
            if gid==None:
                gid=j.application.whoAmI.gid

        key = "%s_%s_%s" % (gid,organization, name)
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)


    # def getJumpscriptFromKey(self, jumpscriptkey, session=None):
    #     if not self.jumpscriptsFromKeys.has_key(jumpscriptkey):
    #         message="Could not find jumpscript with key:%s"%jumpscriptkey
    #         # j.errorconditionhandler.raiseBug(message="Could not find jumpscript with key:%s"%jumpscriptkey,category="jumpscript.controller.scriptnotfound")
    #         raise RuntimeError(message)
    #     return self.jumpscriptsFromKeys[jumpscriptkey]

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

    def executeJumpscript(self, organization, name, role, args={},all=False, timeout=600,wait=True,lock="", session=None):
        """
        @param roles defines which of the agents which need to execute this action
        @all if False will be executed only once by the first found agent, if True will be executed by all matched agents
        """
        self._adminAuth(session.user,session.passwd)

        #action = self.getJumpScript(organization, name)
        if action==None:
            raise RuntimeError("Cannot find jumpscript %s %s"%(organization,name))
        jobs=[]
        role = role.lower()
        if role in self.roles2agents:
            for agentid in self.roles2agents[role]:
                job = Job(self,sessionid=session.id, jsorganization=organization, roles=role, args=json.dumps(args), timeout=timeout, \
                    jscriptid=action.id,lock=lock,jsname=name)
                job.db.nid=int(session.agentid.split("_")[1])
                job.save()
                self.workqueue[agentid].append(job)
                self.jobs[job.db.id]=job
                jobs.append(job)

                if len(self.agent2freeSessions[agentid].keys())>0:
                    #means there are agents waiting for work
                    sessionid=self.agent2freeSessions[agentid].keys()[0]
                    print "found free session:%s"%sessionid
                    self.agent2freeSessions[agentid][sessionid].set()

            if len(jobs)>1:
                jobgroup= Job(self,sessionid=session.id, jsorganization=organization, roles=role, args=json.dumps(args), timeout=timeout, \
                    jscriptid=action.id,lock=lock,jsname=name)
                jobgroup.save()
                for jobchild in jobs:
                    jobgroup.db.children.append(jobchild.db.id)
                    jobgroup.db.childrenActive.append(jobchild.db.id)
                self.jobs[jobgroup.db.id]=jobgroup
                for child in jobs:
                    child=self.jobs[child.db.id]
                    child.db.parent=jobgroup.db.id
                job=jobgroup
                self.jobs[job.db.id]=job
                job.save()

            if wait:
                return self.waitJumpscript(job.db.id,session)

            return job.db.__dict__
        else:
            print "nothingtodo"
            job = Job(self,sessionid=session.id, jsorganization=organization, roles=role, args=json.dumps(args), timeout=timeout, \
                    jscriptid=action.id,lock=lock,jsname=name)
            job.db.state="NOWORK"
            job.db.timeStop=job.db.timeStart

            job.save()            
            return job.db.__dict__

    def waitJumpscript(self,jobid,session):
        """
        @return returncode,result
        returncode 0 = ok
        returncode 1 = timeout
        returncode 2 = error (then result is eco)

        """
        job=self.jobs.get(jobid)
        if not job:
            raise RuntimeError("Not job found with id %s" % jobid)
        timeout = gevent.Timeout(job.db.timeout)
        timeout.start()
        try:
            job.wait()
            timeout.cancel()
            return job.db.__dict__
        except:
            timeout.cancel()
            job.resultcode=1
            print "timeout on execution"
            return job.db.__dict__

    def getWork(self, session=None):
        """
        is for agent to ask for work
        """
        self.sessionsUpdateTime[session.id]=j.base.time.getTimeEpoch()
        # gevent.spawn(greenletGetWork,session=session)
        timeout = gevent.Timeout(30)
        timeout.start()
        try:
            while True:
                if len(self.workqueue[session.agentid])>0:
                    #check locking

                    job=self.workqueue[session.agentid][-1]
                    if job.db.lock and not self.locks.checkLock(session.agentid,job.db.lock):
                        #not set yet can execute
                        job=self.workqueue[session.agentid].pop()
                        self.locks.addLock(session.agentid,job.db.lock,job.db.lockduration)
                    else:
                        job=self.workqueue[session.agentid].pop()
                    self.activeJobSessions[session.id]=job
                    timeout.cancel()
                    return (job.db.jscriptid,job.db.args,job.db.id)
                #else no work wait for x time (to support long polling) to see if there is activity for this session
                event=self._markSessionFree(session)
                print "wait for event for agent:id %s"%session.agentid
                event.wait()
                #if we get here there is someone asking something to do, unmark the session, go into while to return next job
                self._unmarkSessionFree(session)

        except:# Exception,e:
            timeout.cancel()
            #because of timeout max wait is 2 min
            self._unmarkSessionFree(session)
            print "timeout (if too fast timeouts then error in getWork while loop)"

    def notifyWorkCompleted(self,result=None,eco=None,session=None):
        self.sessionsUpdateTime[session.id]=j.base.time.getTimeEpoch()

        if (not self.activeJobSessions.has_key(session.id)) or self.activeJobSessions[session.id]==None:
            raise RuntimeError("Could not notify job completed for session:%s"%session.id)
        
        job = self.activeJobSessions.pop(session.id)
        job.db.timeStop=self.sessionsUpdateTime[session.id]

        if eco:
            job.db.resultcode=2
            job.db.state="ERROR"
            ecobj = j.errorconditionhandler.getErrorConditionObject(eco)
            print "#####ERROR ON AGENT######"
            try:
                j.errorconditionhandler.processErrorConditionObject(ecobj)
            except:
                print ecobj
            print "#########################"
            job.db.result = json.dumps(eco)
        else:
            eco = ''
            job.db.resultcode=0
            job.db.state="OK"
            job.db.result = json.dumps(result)
        job.save()
    
        #now need to return it to the client who asked for the work 
        if job.db.parent and job.db.parent in self.jobs:
            parentjob = self.jobs[job.db.parent]
            parentjob.db.childrenActive.remove(job.db.id)
            if job.db.state == 'ERROR':
                parentjob.db.state = 'ERROR'
                parentjob.db.result = job.db.result
            if not parentjob.db.childrenActive:
                #all children executed
                parentjob.db.resultcode=0
                if parentjob.db.state != 'ERROR':
                    parentjob.db.state = "OK"
                if not parentjob.db.result:
                    parentjob.db.result = json.dumps(None)
                parentjob.save()
                parentjob.done()
        job.done()

        print "completed job"
        print "result was.\n"
        print job.db
        return

    def getScheduledWork(self,agentid,session=None):
        """
        list all work scheduled for 1 agent
        """
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

        result=[]
        if self.workqueue.has_key(session.agentid):
            if len(self.workqueue[session.agentid])>0:
                result=[item.__dict__ for item in self.workqueue[session.agentid]]
        return result

    def log(self, logs, session=None):
        j.logger.logTargetLogForwarder.logBatch(logs)
            

    def listSessions(self,session=None):
        result=[]
        for sessionid, session in self.sessions.iteritems():
            sessionresult={}
            sessionresult["id"]=sessionid
            sessionresult["roles"]=session.roles
            sessionresult["netinfo"]=session.netinfo
            sessionresult["organization"]=session.organization
            sessionresult["agentid"]=session.agentid
            sessionresult["id"]=session.id
            sessionresult["user"]=session.user
            sessionresult["start"]=session.start
            sessionresult["lastpoll"]=self.sessionsUpdateTime[session.id]
            activejob = self.activeJobSessions.get(session.id)
            sessionresult["activejob"] = activejob.id if activejob else None
            result.append(sessionresult)
        return result

    def getJobInfo(self, jobid, session=None):
        job = self.jobs.get(jobid)
        if job:
            return job.db.__dict__

    def getActiveJobs(self, session=None):
        results = list()
        for value in self.activeJobSessions.itervalues():
            results.append(value.db.__dict__)
        return results

    def listJobs(self, session=None):
        """
        list all jobs waiting for which roles, show for each role which agents should be answering
        also list jobs which are running and running in which sessions
        """
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

cmds=daemon.daemon.cmdsInterfaces["agent"][0]
cmds.loadJumpscripts()

daemon.start()


j.application.stop()

