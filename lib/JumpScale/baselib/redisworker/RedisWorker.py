from JumpScale import j
import ujson
import JumpScale.grid.osis
import JumpScale.baselib.redis
OsisBaseObject=j.core.osis.getOsisBaseObjectClass()

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
            if action<>None:
                self.setArgs(action)
            else:
                pass
                # self.args=[]
                # self.argsDefaults = args.defaults
                # self.argsVarArgs = args.varargs
                # self.argsKeywords = args.keywords

            self.source = source
            self.path = path
            self.enabled=True
            self.async=True
            self.period=0
            self.order=0
            self.queue=""

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
        # self.returnqueue=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%self.sessionid)

    def getJob(self, jscriptid=None,args={}, timeout=60,log=True, queue="default",ddict={}):
        job=Job(ddict=ddict, args=args, timeout=timeout, sessionid=self.sessionid, jscriptid=jscriptid,log=log, queue=queue)
        job.id=self.redis.incr("workers:joblastid")      
        job.getSetGuid()
        return job

    def getJumpscriptId(self,name="", category="unknown", organization="unknown", action=None, source="", path="", descr=""):
        js=Jumpscript(name=name, category=category, organization=organization, action=action, source=source, path=path, descr=descr)
        key=js.getContentKey()
        if self.redis.hexists("workers:jumpscripthashes",key):
            return self.redis.hget("workers:jumpscripthashes",key)
        else:
            #jumpscript does not exist yet
            js.id=self.redis.incr("workers:jumpscriptlastid")
            self.redis.hset("workers:jumpscripts",js.id,ujson.dumps(js.__dict__))
            self.redis.hset("workers:jumpscripthashes",key,js.id)
            return js.id

    def getJumpscriptFromId(self,jscriptid):
        jsdict=self.redis.hget("workers:jumpscripts",jscriptid)
        if jsdict:
                jsdict=ujson.loads(jsdict)
            else:
                raise RuntimeError("cannot find jumpscript with id:%s"%jsdict)
        return Jumpscript(ddict=jsdict)
        
    def execFunctionSync(self,method,_category="unknown", _organization="unknown",_timeout=60,_queue="default",_log=True,**args):
        jsid=self.getJumpscriptId(action=method,category=_category,organization=_organization)
        job=self.getJob(jsid,args=args,timeout=_timeout,log=_log,queue=_queue)
        self.scheduleJob(job)
        return self.waitJob(self,job.id)

    def getReturnQueue(self,jobid):
        # if not self.returnQueues.has_key(jobid):
            # self.returnQueues[jobid]=j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%self.jobid)
        # return self.returnQueues[jobid]
        return j.clients.redis.getGeventRedisQueue("127.0.0.1",7768,"workers:return:%s"%jobid)


    def getWork(self,qname,timeout=0):
        if not self.queue.has_key(qname):
            raise RuntimeError("Could not find queue to execute job:%s ((ops:workers.schedulework L:1))"%job)
        queue=self.queue[qname]        
        if timeout<>0:
            jobid=queue.get(timeout=60)
        else:
            jobid=queue.get()
        if jobid<>None:
            jobdict=self.redis.hget("workers:jobs",jobid)
            if jobdict:
                    jobdict=ujson.loads(jobdict)
                else:
                    raise RuntimeError("cannot find job with id:%s"%jobid)
            return getJob(ddict=jobdict)

    def waitJob(self,jobid,timeout=600):
        q=self.getReturnQueue(jobid)        
        result=q.get(timeout=timeout)
        from IPython import embed
        print "DEBUG NOW ooo"
        embed()
        
    def scheduleJob(self,job):
        qname=job.queue
        if not qname or qname.strip()=="":
            qname="default"

        if not self.queue.has_key(qname):
            raise RuntimeError("Could not find queue to execute job:%s ((ops:workers.schedulework L:1))"%job)

        queue=self.queue[qname]

        # result = queue.enqueue_call('%s_%s.action'%(job["category"],job["cmd"]),kwargs=job["args"],\
        #     timeout=int(job["timeout"]))
        self.redis.hset("workers:jobs",job.id, ujson.dumps(job))
        queue.put(job.id)
        # q=self.getReturnQueue(job.id)

