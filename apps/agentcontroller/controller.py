
from JumpScale import j

import JumpScale.grid.geventws
import gevent
from gevent.event import Event
import copy

j.application.start("agentcontroller")

j.logger.consoleloglevel = 2

import inspect


class Jumpscript():

    def __init__(self, name, category, organization, author, license, version, roles, action, source, path, descr):
        self.name = name
        self.descr = descr
        self.category = category
        self.organization = organization
        self.author = author
        self.license = license
        self.version = version
        self.roles = roles
        args = inspect.getargspec(action)
            # args.args.remove("session")
            # methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        self.args = args.args
        self.argsDefaults = args.defaults
        self.argsVarArgs = args.varargs
        self.argsKeywords = args.keywords
        self.source = source
        self.path = path
        self.id = j.base.byteprocessor.hashTiger160(str([source, roles]))  # need to make sure roles & source cannot be changed

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__

class Job():
    def __init__(self, sessionid,jsname, jsorganization, roles,args,timeout,jscriptid):
        self.id= j.base.idgenerator.generateGUID()
        self.jsname = jsname
        self.jsorganization=jsorganization
        self.roles=roles
        self.args=args
        self.timeout=timeout
        self.result=None
        self.sessionid=sessionid
        self.jscriptid=jscriptid
        self.event=None
        self.children=[]
        self.childrenActive={}
        self.parent=None
        self.resultcode=None

    def __repr__(self):
        return str(self.__dict__)

    __str__ = __repr__

class ControllerCMDS():

    def __init__(self, daemon):
        self.daemon = daemon
        self.jumpscripts = {}
        self.jumpscriptsFromKeys = {}

        self.workqueue = {}  # key=agentid

        self.jobs= {} #key is jobid

        self.roles2agents = {}  # key=role in all depths

        self.session2agent={} #key= sessionid, val = agentid
        self.agent2sessions={} #key=agent, val=list of sessions
        self.sessions={} #key=sessionid
        self.sessionsUpdateTime={} #key=sessionid, val is last epoch of contact
        self.activeJobSessions={}  # key=sessionid , is job running per session or does not exist if no job running on that session
        
        self.agent2freeSessions={} #key is agent, val is dict of sessions free to be used

        self.adminpasswd = "1234"

    def _adminAuth(self,user,passwd):
        if (user=="admin" and passwd==self.adminpasswd)==False:
            raise RuntimeError("permission denied")

    def authenticate(self, session):
        return True  # will authenticall all (is std)

    def _setRole2Agent(self,role,agent):
        if not self.roles2agents.has_key(role):
            self.roles2agents[role]=[]
        if agent not in self.roles2agents[role]:
            self.roles2agents[role].append(agent)   

    def _removeSession(self,sessionid):
        """
        when remote agent is gone (eg. crashed), we need to make sure there are no sessions and other params in mem
        """
        session=self.sessions[sessionid]
        self.sessions.pop(sessionid)
        w=self.agent2sessions[session.agentid]
        if session.id in w:
            w.remove(session.id)

        w=self.agent2freeSessions[session.agentid]
        if session.id in w.keys():
            toremove=w.pop(session.id)
            toremove.set()
            
        for job in self.activeJobSessions.itervalues():
            if job.sessionid==sessionid:
                print "found job which cannot be completed" #@todo need to escalate
                self.activeJobSessions.pop(job.sessionid)
            self.jobs.pop(job.id)
            del job

        if self.session2agent.has_key(session.id):
            self.session2agent.pop(session.id)

        if self.sessionsUpdateTime.has_key(session.id):
            self.sessionsUpdateTime.pop(session.id)

        del session

        #@todo check all is indeed removed from mem

    def _clean(self,similarProcessPIDs,session):
        print similarProcessPIDs        
        pid=int(session.id.split("_")[2])
        
        similarProcessPIDs.pop(similarProcessPIDs.index(pid))
        if self.agent2sessions.has_key(session.agentid):
            for sessionkey in self.agent2sessions[session.agentid]:
                session=self.sessions[sessionkey]
                pidinmem=int(session.id.split("_")[3])
                print "pidinmem:%s for agent:%s"%(pidinmem,session.agentid)
                if pidinmem not in similarProcessPIDs:
                    #session no longer valid, remove
                    self._removeSession(session.id)

    def register(self, similarProcessPIDs,session):
        self._clean(similarProcessPIDs,session)
        self.sessions[session.id]=session
        self.session2agent[session.id]=session.agentid
        roles=session.roles
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
            from IPython import embed
            print "DEBUG NOW bug in _unmarksessionfree of agentcontroller, need to fix"
            embed()
            
        if self.agent2freeSessions[session.agentid].has_key(session.id):
            self.agent2freeSessions[session.agentid].pop(session.id)

    def escalateError(self,eco):
        from IPython import embed
        print "DEBUG NOW eco escalate"
        embed()        

    def loadJumpscripts(self, path="jumpscripts", session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        for path2 in j.system.fs.listFilesInDir(path=path, recursive=True, filter="*.py", followSymlinks=True):
            C = j.system.fs.fileGetContents(path2)
            C2 = ""
            name = ""
            category = "unknown"
            organization = "unknown"
            author = "unknown"
            license = "unknown"
            version = "1.0"
            roles = ["*"]
            source = ""

            state = "start"

            for line in C.split("\n"):
                line = line.replace("\t", "    ")
                line = line.rstrip()
                if line.strip() == "":
                    continue
                if line.find("###########") != -1:
                    break
                C2 += "%s\n" % line
                if state == "start" and line.find("def action") == 0:
                    state = "action"
                if state == "action":
                    source += "%s\n" % line

            try:
                exec(C2)
            except Exception as e:
                msg="Could not load jumpscript:%s\n" % path2
                msg+="Error was:%s\n" % e
                # print msg
                j.errorconditionhandler.raiseInputError(msgpub="",message=msg,category="agentcontroller.load",tags="",die=False)
                continue

            t = Jumpscript(name, category, organization, author, license, version, roles, action, source, path2, descr)
            print "found jumpscript:%s " %("%s_%s" % (organization, name))
            self.jumpscripts["%s_%s" % (organization, name)] = t
            self.jumpscriptsFromKeys[t.id] = t
        
    def getJumpscript(self, organization, name, session=None):
        if session<>None:
            self._adminAuth(session.user,session.passwd)
        key = "%s_%s" % (organization, name)
        if key in self.jumpscripts:
            return self.jumpscripts[key]
        else:
            j.errorconditionhandler.raiseOperationalCritical("Cannot find jumpscript %s:%s" % (organization, name), category="action.notfound", die=False)

    def getJumpscriptFromKey(self, jumpscriptkey, session=None):
        if not self.jumpscriptsFromKeys.has_key(jumpscriptkey):
            message="Could not find jumpscript with key:%s"%jumpscriptkey
            # j.errorconditionhandler.raiseBug(message="Could not find jumpscript with key:%s"%jumpscriptkey,category="jumpscript.controller.scriptnotfound")
            raise RuntimeError(message)
        return self.jumpscriptsFromKeys[jumpscriptkey]

    def listJumpscripts(self, organization=None, cat=None, session=None):
        """
        @return [[org,name,category,descr],...]
        """
        if session<>None:
            self._adminAuth(session.user,session.passwd)

        result = []
        for key in self.jumpscripts.keys():
            t = self.jumpscripts[key]
            match = False
            if organization == None:
                match = True
            else:
                match = organization == t.organization
            if cat != None and match:
                match = cat == t.category
            if match:
                result.append([t.organization, t.name, t.category, t.descr])
        return result

    def executeJumpscript(self, organization, name, role, args={},all=False, timeout=600,session=None,wait=True):
        """
        @param roles defines which of the agents which need to execute this action
        @all if False will be executed only once by the first found agent, if True will be executed by all matched agents
        """
        self._adminAuth(session.user,session.passwd)

        action = self.getJumpscript(organization, name)
        if action==None:
            raise RuntimeError("Cannot find jumpscript %s %s"%(organization,name))
        jobs=[]
        if self.roles2agents.has_key(role):
            for agentid in self.roles2agents[role]:
                job=Job(session.id,name,organization,role,args,timeout,jscriptid=action.id)
                self.workqueue[agentid].append(job)
                self.jobs[job.id]=job
                jobs.append(job.id)

                if len(self.agent2freeSessions[agentid].keys())>0:
                    #means there are agents waiting for work
                    sessionid=self.agent2freeSessions[agentid].keys()[0]
                    print "found free session:%s"%sessionid
                    self.agent2freeSessions[agentid][sessionid].set()

            if len(jobs)>1:
                jobgroup=Job(None,name,organization,role,args,timeout,jscriptid=action.id)
                jobgroup.children=jobs
                self.jobs[jobgroup.id]=jobgroup
                for childid in jobs:
                    child=self.jobs[childid]
                    child.parent=jobgroup
                job=jobgroup

            if wait:
                return self.waitJumpscript(job.id,session)

            job2=copy.copy(job)
            job2.__dict__.pop("event")
            return job2


    def waitJumpscript(self,jobid,session):
        """
        @return returncode,result
        returncode 0 = ok
        returncode 1 = timeout
        returncode 2 = error (then result is eco)

        """
        print "wait job execution:%s"%jobid
        job=self.jobs[jobid]
        timeout = gevent.Timeout(job.timeout)
        timeout.start()
        try:
            job.event=Event()
            job.event.wait()            
            timeout.cancel()
            job.__dict__.pop("event")
            return job.__dict__
        except:
            timeout.cancel()
            job.resultcode=1
            print "timeout on execution"
            job.__dict__.pop("event")
            return job.__dict__


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
                    job=self.workqueue[session.agentid].pop()
                    self.activeJobSessions[session.id]=job
                    timeout.cancel()
                    return (job.jscriptid,job.args)
                #else no work wait for x time (to support long polling) to see if there is activity for this session
                event=self._markSessionFree(session)
                print "wait for event for agent:id %s"%session.agentid
                event.wait()
                #if we get here there is someone asking something to do, unmark the session, go into while to return next job
                self._unmarkSessionFree(session)

        except:
            timeout.cancel()
            #because of timeout max wait is 2 min
            self._unmarkSessionFree(session)
            print "timeout"


    def notifyWorkCompleted(self,result=None,eco=None,session=None):
        # print "notifyworkcompleted"
        self.sessionsUpdateTime[session.id]=j.base.time.getTimeEpoch()

        if (not self.activeJobSessions.has_key(session.id)) or self.activeJobSessions[session.id]==None:
            raise RuntimeError("Could not notify job completed for session:%s"%session.id)
        
        job= self.activeJobSessions.pop(session.id)

        if eco<>None:
            job.result=eco
            job.resultcode=2
        else:   
            job.result=result
        
        #now need to return it to the client who asked for the work 
        if job.parent<>None:
            job.parent.childrenActive.pop(job.id)
            if len(job.parent.childrenActive)==0:
                #all children executed
                job.parent.event.set()
        
        # if job.event<>None:
        job.event.set()

        print "completed job"
        # print "result was.\n"
        # print job.
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


# will reinit for testing everytime, not really needed
# j.servers.geventws.initSSL4Server("myorg", "controller1")

daemon = j.servers.geventws.getServer(port=4444)

daemon.addCMDsInterface(ControllerCMDS, category="agent")  # pass as class not as object !!! chose category if only 1 then can leave ""

cmds=daemon.daemon.cmdsInterfaces["agent"][0]
cmds.loadJumpscripts()

daemon.start()


j.application.stop()
