from JumpScale import j
import ujson
import JumpScale.grid.osis
import JumpScale.baselib.redis
OsisBaseObject=j.core.osis.getOsisBaseObjectClass()
import time

class Job(OsisBaseObject):

    """
    identifies a job in the grid
    """

    def __init__(self, ddict={},args={}, timeout=60, sessionid=None, jscriptid=None,cmd="",category="",log=True, queue=None):
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.sessionid = sessionid
            self.gid =j.application.whoAmI.gid
            self.nid =j.application.whoAmI.nid
            self.cmd = cmd
            self.category = category
            self.jscriptid=jscriptid
            self.roles=[]
            self.args=args
            self.queue=queue
            self.timeout=timeout
            self.result=None
            self.parent=None
            self.resultcode=None
            self.state="SCHEDULED" #SCHEDULED,STARTED,ERROR,OK,NOWORK
            self.timeStart=j.base.time.getTimeEpoch()
            self.timeStop=0
            self.log=log

    def getSetGuid(self):
        self.guid = "%s_%s_%s" % (self.gid, self.nid,self.id)
        return self.guid

class Jumpscript(OsisBaseObject):

    """
    identifies a Jumpscript in the grid
    """

    def __init__(self, ddict={},name="", category="", organization="", action=None, source="", path="", descr=""):
        
        if ddict <> {}:
            self.load(ddict)
        else:
            self.id=0
            self.gid =j.application.whoAmI.gid
            self.name = name
            self.descr = descr
            self.category = category
            self.organization = organization
            self.author = ""
            self.license = ""
            self.version = ""
            self.roles = []
   
            self.source = source
            self.path = path
            self.enabled=True
            self.async=True
            self.period=0
            self.order=0
            self.queue=""
            self.log=True

            if action<>None:
                self.setArgs(action)
            else:
                pass
                # self.args=[]
                # self.argsDefaults = args.defaults
                # self.argsVarArgs = args.varargs
                # self.argsKeywords = args.keywords

       
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
        if self.name=="":
            self.name=action.func_name
        if self.organization=="":
            from IPython import embed
            print "DEBUG NOW uuuorg setArgs redisworker"
            embed()
            
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
        out=""
        for item in ["name","category","args","source"]:
            out+=str(self.__dict__[item])
        return j.tools.hash.md5_string(out)

class RedisWorkerFactory:
    """
    """

    def __init__(self):
        self.redis=j.clients.redis.getGeventRedisClient("127.0.0.1", 7768)
        self.sessionid=j.base.idgenerator.generateRandomInt(1,1000000)

        self.returnQueues={}

        session={"start":j.base.time.getTimeEpoch()}
        session["gid"]=j.application.whoAmI.gid
        session["nid"]=j.application.whoAmI.nid
        session["pid"]=j.application.whoAmI.pid
        session["appname"]=j.application.appname
        self.redis.hset("workers:sessions",self.sessionid,ujson.dumps(session))

        #local jumpscripts start at 10000
        if not self.redis.exists("workers:jumpscriptlastid") or int(self.redis.get("workers:jumpscriptlastid"))<10000:
            self.redis.set("workers:jumpscriptlastid",10000)

        self.queue={}
        self.queue["io"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:io")
        self.queue["hypervisor"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:hypervisor")
        self.queue["default"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:default")
        self.queue["process"] = j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:work:process")
        # self.returnqueue=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%self.sessionid)

    def _getJob(self, jscriptid=None,args={}, timeout=60,log=True, queue="default",ddict={}):
        job=Job(ddict=ddict, args=args, timeout=timeout, sessionid=self.sessionid, jscriptid=jscriptid,log=log, queue=queue)
        job.id=self.redis.incr("workers:joblastid")      
        job.getSetGuid()
        return job

    def getJob(self,jobid):
        jobdict=self.redis.hget("workers:jobs",jobid)
        if jobdict:
            jobdict=ujson.loads(jobdict)
        else:
            raise RuntimeError("cannot find job with id:%s"%jobid)
        return jobdict

    def _getJumpscript(self,name="", category="unknown", organization="unknown", action=None, source="", path="", descr=""):
        js=Jumpscript(name=name, category=category, organization=organization, action=action, source=source, path=path, descr=descr)
        key=js.getContentKey()
        if self.redis.hexists("workers:jumpscripthashes",key):
            jumpscript_data=self.redis.hget("workers:jumpscripthashes",key)
            js=Jumpscript(ddict=ujson.loads(jumpscript_data))
        else:
            #jumpscript does not exist yet
            js.id=self.redis.incr("workers:jumpscriptlastid")
            jumpscript_data=ujson.dumps(js.__dict__)
            self.redis.hset("workers:jumpscripts:id",js.id, js)
            if js.organization<>"" and js.name<>"":
                self.redis.hset("workers:jumpscripts:name","%s__%s"%(js.organization,js.name), jumpscript_data)            
            self.redis.hset("workers:jumpscripthashes",key,jumpscript_data)
        return js

    def getJumpscriptFromId(self,jscriptid):
        jsdict=self.redis.hget("workers:jumpscripts:id",jscriptid)
        if jsdict:
            jsdict=ujson.loads(jsdict)
        else:
            raise RuntimeError("Cannot find jumpscript with id:%s"%jscriptid)
        return Jumpscript(ddict=jsdict)

    def getJumpscriptFromName(self,organization,name):
        key="%s__%s"%(organization,name)
        jsdict=self.redis.hget("workers:jumpscripts:name",key)
        if jsdict:
            jsdict=ujson.loads(jsdict)
        else:
            return None
        return Jumpscript(ddict=jsdict)        
        
    def execFunction(self,method,_category="unknown", _organization="unknown",_timeout=60,_queue="default",_log=True,_sync=True,**args):
        """
        @return job
        """
        js=self._getJumpscript(action=method,category=_category,organization=_organization)
        jsid=js.id
        job=self._getJob(jsid,args=args,timeout=_timeout,log=_log,queue=_queue)
        job.cmd=js.name
        self._scheduleJob(job)
        if _sync:
            job=self.waitJob(job,timeout=_timeout)
        return job

    def execJumpscript(self,jumpscriptid=None,jumpscript=None,_timeout=60,_queue="default",_log=True,_sync=True,**args):
        """
        @return job
        """
        js=jumpscript
        if js==None:
            js=self.getJumpscriptFromId(jumpscriptid)
        else:
            js = jumpscript
        job=self._getJob(js.id,args=args,timeout=_timeout,log=_log,queue=_queue)
        job.cmd="%s/%s"%(js.organization,js.name)
        job.category="jumpscript"
        job.log=js.log
        self._scheduleJob(job)
        if _sync:
            job=self.waitJob(job,timeout=_timeout)
        return job   

    def execJobAsync(self,job):
        print "execJobAsync:%s"%job["id"]
        job=Job(ddict=job)
        self._scheduleJob(job)
        return job

    def _getWork(self,qname,timeout=0):
        if not self.queue.has_key(qname):
            raise RuntimeError("Could not find queue to execute job:%s ((ops:workers.schedulework L:1))"%qname)
        queue=self.queue[qname]
        if timeout<>0:
            jobdict=queue.get(timeout=timeout)
        else:
            jobdict=queue.get()
        if jobdict<>None:   
            jobdict=ujson.loads(jobdict)         
            return Job(ddict=jobdict)
        return None

    def waitJob(self,job,timeout=600):
        result=self.redis.blpop("workers:return:%s"%job.id, timeout=timeout)        
        if result==None:            
            job.state="TIMEOUT"
            job.timeStop=int(time.time())
            self.redis.hset("workers:jobs",job.id, ujson.dumps(job.__dict__))
            j.events.opserror("timeout on job:%s"%job, category='workers.job.wait.timeout', e=None)
        else:
            job=self.getJob(job.id)

        if job.state<>"OK":
            raise RuntimeError("could not execute job:%s error was:%s"%(job.id,job.result))

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

        # self.redis.hset("workers:jobs",job.id, ujson.dumps(job.__dict__))
        queue.put(job)

    def scheduleJob(self, job):
        jobobj = Job(ddict=job)
        self._scheduleJob(jobobj)

    def getJobLine(self,job=None,jobid=None):
        if jobid<>None:
            job=self.getJob(jobid)
        start=j.base.time.epoch2HRDateTime(job.timeStart)
        if job.timeStop==0:
            stop=""
        else:
            stop=j.base.time.epoch2HRDateTime(job.timeStop)
        line="|%s|%s|%s|%s|%s|%s|%s|%s|"%(job.id,job.jscriptid,job.category,job.cmd,start,stop,job.state,job.queue)
        return line


    def getQueuedJobs(self, queue=None, asWikiTable=True):
        result = list()
        queues = [queue] if queue else ["io","hypervisor","default"]
        for item in queues:
            jobs = self.redis.lrange('queues:workers:work:%s' % item, 0, -1)
            for jobstring in jobs:
                result.append(ujson.loads(jobstring))
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
                jobs.append(ujson.loads(jobstring))

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
                jobs.update(ujson.loads(jobsjson))
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
