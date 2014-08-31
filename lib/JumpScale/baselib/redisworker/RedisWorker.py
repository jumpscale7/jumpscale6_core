from JumpScale import j
try:
    import ujson as json
except:
    import json

import JumpScale.baselib.hash
import JumpScale.grid.osis
import JumpScale.baselib.redis
OsisBaseObject=j.core.osis.getOsisBaseObjectClass()
import time
import inspect

# if j.application.config.exists("agentcontroller.webdiskey"):
import JumpScale.grid.jumpscripts
Jumpscript=j.tools.jumpscriptsManager.getJSClass()
# else:
    # Jumpscript=None

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={},args={}, timeout=60, sessionid=None, jscriptid=None,cmd="",category="",log=True, queue=None, wait=False):
        self.errorreport = False
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.sessionid = sessionid
            self.gid =j.application.whoAmI.gid
            self.nid =j.application.whoAmI.nid
            self.cmd = cmd
            self.wait = wait
            self.category = category
            self.jscriptid=jscriptid
            self.roles=[]
            self.args=args
            self.queue=queue
            self.errorreport = False
            self.timeout=timeout
            self.result=None
            self.parent=None
            self.resultcode=None
            self.state="SCHEDULED" #SCHEDULED,STARTED,ERROR,OK,NOWORK
            self.timeStart=j.base.time.getTimeEpoch()
            self.timeStop=0
            self.log=log

    def setArgs(self,action):
        import inspect
        args = inspect.getargspec(action)
            # args.args.remove("session")
            # methods[name] = {'args' : args, 'doc': inspect.getdoc(method)}
        self.args = args.args
        self.argsDefaults = args.defaults
        self.argsVarArgs = args.varargs
        self.argsKeywords = args.keywords
        source=inspect.getsource(action)
        splitted=source.split("\n")
        splitted[0]=splitted[0].replace(action.func_name,"action")
        self.source="\n".join(splitted)
            
    def getSetGuid(self):
        """
        use osis to define & set unique guid (sometimes also id)
        """
        self.gid = int(self.gid)
        self.id = int(self.id)
        self.guid = j.base.byteprocessor.hashTiger160(self.getContentKey())  # need to make sure roles & source cannot be changed

        return self.guid

    def getContentKey(self):
        """
        is like returning the hash, is used to see if object changed
        """
        # out=""
        # for item in ["cmd","category","args","source"]:
        #     out+=str(self.__dict__[item])
        return j.tools.hash.md5_string(str(self.__dict__))

class RedisWorkerFactory:
    """
    """

    def __init__(self):
        self.redis=j.clients.redis.getGeventRedisClient("127.0.0.1", 7768)
        random = j.base.idgenerator.generateGUID()
        self.sessionid="%s_%s_%s_%s"%(j.application.whoAmI.gid,j.application.whoAmI.nid,j.application.whoAmI.pid, random)

        self.returnQueues={}

        # session={"start":j.base.time.getTimeEpoch()}
        # session["gid"]=j.application.whoAmI.gid
        # session["nid"]=j.application.whoAmI.nid
        # session["pid"]=j.application.whoAmI.pid
        # session["appname"]=j.application.appname
        # self.redis.hset("workers:sessions",self.sessionid,json.dumps(session))
        self.redis.delete("workers:sessions")

        #local jumpscripts start at 10000
        if not self.redis.exists("workers:jumpscriptlastid") or int(self.redis.get("workers:jumpscriptlastid"))<1000000:
            self.redis.set("workers:jumpscriptlastid",1000000)

        if self.redis.get("workers:joblastid")==None or int(self.redis.get("workers:joblastid"))>500000:
            self.redis.set("workers:joblastid",1)

        self.queue={}
        self.queue["io"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:io")
        self.queue["hypervisor"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:hypervisor")
        self.queue["default"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:default")
        self.queue["process"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:process")
        # self.returnqueue=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%self.sessionid)

    def useCRedis(self):
        self.redis=j.clients.credis.getRedisClient("127.0.0.1", 7768)

    def _getJob(self, jscriptid=None,args={}, timeout=60,log=True, queue="default",ddict={}):
        job=Job(ddict=ddict, args=args, timeout=timeout, sessionid=self.sessionid, jscriptid=jscriptid,log=log, queue=queue)
        job.id=self.redis.incr("workers:joblastid")      
        job.getSetGuid()
        return job

    def getJob(self,jobid):
        jobdict=self.redis.hget("workers:jobs",jobid)
        if jobdict:
            jobdict=json.loads(jobdict)
        else:
            raise RuntimeError("cannot find job with id:%s"%jobid)
        return jobdict


    def getJumpscriptFromId(self,jscriptid):
        jsdict=self.redis.hget("workers:jumpscripts:id",jscriptid)
        if jsdict:
            jsdict=json.loads(jsdict)
        else:
            return None
        
        return Jumpscript(ddict=jsdict)

    def deleteJumpscripts(self):
        for item in ["workers:jumpscripts:id","workers:jumpscripts:name"]:
            self.redis.delete(item)

    def deleteQueues(self):
        for item in ["queues:workers:work:process","queues:workers:work:io","queues:workers:work:hypervisor","queues:workers:work:default"]:
            self.redis.delete(item)

    def deleteProcessQueue(self):
        for item in ["queues:workers:work:process","workers:inqueuetest"]:
            self.redis.delete(item)

    def getJumpscriptFromName(self,organization,name):
        key="%s__%s"%(organization,name)
        jsdict=self.redis.hget("workers:jumpscripts:name",key)
        if jsdict:
            jsdict=json.loads(jsdict)
        else:
            return None
        return Jumpscript(ddict=jsdict)        
        
    def execFunction(self,method,_category="unknown", _organization="unknown",_timeout=60,_queue="default",_log=True,_sync=True,**args):
        """
        @return job
        """
        source=inspect.getsource(method)
        first=True
        for line in source.split("\n"):
            if first:
                orglen=len(line)
                line=line.lstrip()
                newlen=len(line)
                removeNrChars=orglen-newlen                
                methodstr=line.split(" ")[1]                
                name,remainder=methodstr.split("(",1)
                name=name.strip()
                lines=["def action(%s"%(remainder)]
                first=False
            else:        
                line=line[removeNrChars:]
                lines.append(line)
        source="\n".join(lines)

        js=Jumpscript()
        js.source=source
        js.organization=_organization
        js.name=name
        key=j.tools.hash.md5_string(source)

        if self.redis.hexists("workers:jumpscripthashes",key):
            js.id=self.redis.hget("workers:jumpscripthashes",key)
            # js=Jumpscript(ddict=json.loads(jumpscript_data))
        else:
            #jumpscript does not exist yet
            js.id=self.redis.incr("workers:jumpscriptlastid")
            jumpscript_data=json.dumps(js.__dict__)
            self.redis.hset("workers:jumpscripts:id",js.id, jumpscript_data)
            if js.organization<>"" and js.name<>"":
                self.redis.hset("workers:jumpscripts:name","%s__%s"%(js.organization,js.name), jumpscript_data)            
            self.redis.hset("workers:jumpscripthashes",key,js.id)

        job=self._getJob(js.id,args=args,timeout=_timeout,log=_log,queue=_queue)
        job.cmd=js.name
        self._scheduleJob(job)
        if _sync:
            job=self.waitJob(job,timeout=_timeout)
            return job.result            
        else:
            return job

    def checkJumpscriptQueue(self,jumpscript,queue):
        """
        this checks that jumpscripts are not executed twice when being scheduled recurring
        one off jobs will always execute !!!
        """
        if jumpscript.period>0:
            #check of already in queue
            if self.redis.hexists("workers:inqueuetest",jumpscript.getKey()):
                inserttime=int(self.redis.hget("workers:inqueuetest",jumpscript.getKey()))
                if inserttime<(int(time.time())-3600): #when older than 1h remove no matter what
                    self.redis.hdel("workers:inqueuetest",jumpscript.getKey())
                    self.checkQueue()                
                    return False
                print "%s is already scheduled"%jumpscript.name
                return True                
        return False

    def execJumpscript(self,jumpscriptid=None,jumpscript=None,_timeout=60,_queue="default",_log=True,_sync=True,**args):
        """
        @return job
        """
        js=jumpscript
        if js==None:
            js=self.getJumpscriptFromId(jumpscriptid)
        else:
            js = jumpscript
        if self.checkJumpscriptQueue(js,_queue):
            return None
        job=self._getJob(js.id,args=args,timeout=_timeout,log=_log,queue=_queue)
        job.cmd="%s/%s"%(js.organization,js.name)
        job.category="jumpscript"
        job.log=js.log
        self._scheduleJob(job)
        self.redis.hset("workers:inqueuetest",js.getKey(),int(time.time()))
        if _sync:
            job=self.waitJob(job,timeout=_timeout)
        return job   

    def execJobAsync(self,job):
        print "execJobAsync:%s"%job["id"]
        job=Job(ddict=job)
        self._scheduleJob(job)
        return job

    def checkQueue(self):
        return
        db=self.redis
        for name in ["process","hypervisor","default","io"]:
            qname="queues:workers:work:%s"%name
            for i in range (db.llen(qname)):
                jobbin=db.lindex(qname,i)
                print jobbin
        #@todo needs to be implement, need to check there are no double recurring jobs, need to check jumpscripts exist, need to check jobs are also in redis, ...


    def _getWork(self,qname,timeout=0):
        if not self.queue.has_key(qname):
            raise RuntimeError("Could not find queue to execute job:%s ((ops:workers.schedulework L:1))"%qname)
        queue=self.queue[qname]

        if timeout<>0:
            jobdict=queue.get(timeout=timeout)
        else:
            jobdict=queue.get()
        if jobdict<>None:   
            jobdict=json.loads(jobdict)         
            return Job(ddict=jobdict)
        return None

    def waitJob(self,job,timeout=600):
        result=self.redis.blpop("workers:return:%s"%job.id, timeout=timeout)        
        if result==None:            
            job.state="TIMEOUT"
            job.timeStop=int(time.time())
            self.redis.hset("workers:jobs",job.id, json.dumps(job.__dict__))
            j.events.opserror("timeout on job:%s"%job, category='workers.job.wait.timeout', e=None)
        else:
            job=self.getJob(job.id)

        job=Job(ddict=job)
        if job.state<>"OK":
            eco=j.errorconditionhandler.getErrorConditionObject(ddict=job.result)
            # j.errorconditionhandler.processErrorConditionObject(eco)
            raise RuntimeError("Could not execute job, error:\n%s"%str(eco))  #@todo is printing too much
        return job

    def _scheduleJob(self, job):
        """
        """

        qname=job.queue
        if not qname or qname.strip()=="":
            qname="default"

        if not self.queue.has_key(qname):
            raise RuntimeError("Could not find queue to execute job:%s ((ops:workers.schedulework L:1))"%job)

        queue=self.queue[qname]

        # if not self.jobExistsInQueue(qname,job):
            # self.redis.hset("workers:jobs",job.id, json.dumps(job.__dict__))
        queue.put(job)

    def scheduleJob(self, job):
        jobobj = Job(ddict=job)
        self._scheduleJob(jobobj)

    def getJobLine(self,job=None,jobid=None):
        if jobid<>None:
            job=self.getJob(jobid)
        start=j.base.time.epoch2HRDateTime(job['timeStart'])
        if job['timeStop']==0:
            stop="N/A"
        else:
            stop=j.base.time.epoch2HRDateTime(job['timeStop'])
        jobid = '[%s|/grid/job?id=%s]' % (job['id'], job['id'])
        line="|%s|%s|%s|%s|%s|%s|%s|%s|" % (jobid, job['state'], job['queue'], job['category'], job['cmd'], job['jscriptid'], start, stop)
        return line


    def getQueuedJobs(self, queue=None, asWikiTable=True):
        result = list()
        queues = [queue] if queue else ["io","hypervisor","default"]
        for item in queues:
            jobs = self.redis.lrange('queues:workers:work:%s' % item, 0, -1)
            for jobstring in jobs:
                result.append(json.loads(jobstring))
        if asWikiTable:
            out=""
            for job in result:
                out+="%s\n"%self.getJobLine(job=job)
            return out
        return result

    def getFailedJobs(self, queue=None, hoursago=0):
        jobs = list()
        queues = (queue,) if queue else ('io', 'hypervisor', 'default')
        for q in queues:
            jobsjson = self.redis.lrange('queues:workers:work:%s' % q, 0, -1)
            for jobstring in jobsjson:
                jobs.append(json.loads(jobstring))

        #get failed jobs
        for job in jobs:
            if job['state'] not in ('ERROR', 'TIMEOUT'):
                jobs.remove(job)

        if hoursago:
            epochago = j.base.time.getEpochAgo(str(hoursago))
            for job in jobs:
                if job['timeStart'] <= epochago:
                    jobs.remove(job)
        return jobs

    def removeJobs(self, hoursago=48, failed=False):
        epochago = j.base.time.getEpochAgo(hoursago)
        for q in ('io', 'hypervisor', 'default'):
            jobs = dict()
            jobsjson = self.redis.hgetall('queues:workers:work:%s' % q)
            if jobsjson:
                jobs.update(json.loads(jobsjson))
                for k, job in jobs.iteritems():
                    if job['timeStart'] >= epochago:
                        jobs.pop(k)

                if not failed:
                    for k, job in jobs.iteritems():
                        if job['state'] in ('ERROR', 'TIMEOUT'):
                            jobs.pop(k)

                if jobs:
                    self.redis.hdel('queues:workers:work:%s' % q, jobs.keys())

    def deleteJob(self, jobid):
        job = self.getJob(jobid)
        self.redis.hdel('queues:workers:work:%s' % job.queue, jobid)
